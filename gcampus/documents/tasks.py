#  Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["render_cached_document_view", "render_document_to_model"]

import logging
import time
from io import BytesIO
from typing import Type, Union, Tuple

from celery import shared_task
from django.conf import settings
from django.contrib.staticfiles.utils import get_files
from django.core.files import File
from django.core.files.storage import default_storage, Storage
from django.db.models import Model, Q, Manager
from django.db.models.fields.files import FieldFile
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.module_loading import import_string
from django.views import View

from gcampus.auth.models import Course
from gcampus.core.files import file_exists
from gcampus.core.models import Measurement
from gcampus.documents.document import as_bytes_io, render_document_from_html
from gcampus.tasks.lock import redis_lock

logger = logging.getLogger("gcampus.documents.tasks")


def get_document_lock_name(model: type[Model] | str, pk) -> str:
    """Get the lock name for building or modifying the document of a
    certain database row.

    :param model: Model (and thereby table) of the document.
    :param pk: Primary key of the row related to the document.
    """
    if isinstance(model, str):
        model: type[Model] = import_string(model)
    if not issubclass(model, Model):
        raise ValueError(f"'{model}' is not a valid model")
    return f"document_{model.objects.model._meta.db_table}_{pk}"


@shared_task
def render_cached_document_view(
    view: Union[str, Type[View]],
    instance: Union[Model, int],
    language: str,
    force: bool = True,
):
    """Render Cached Document View

    Task to render the document for a given :class:`CachedDocumentView`
    and its instance. The document will be rendered and saved to the
    instance's ``model_file_field``.

    To make this work, a fake mock view will be created alongside a mock
    request.

    :param view: Subclass of :class:`CachedDocumentView`.
    :param language: Language
    :param instance: Optional model instance. If no instance is
        provided, the primary key has to be passed using
        ``instance_pk``.

    :param force: Force document rebuild even if document is already
        saved in the model.
    """
    # Overwrite language to export all files in the default project
    # language for now. Caching different documents for each language
    # should be implemented at some point.
    language: str = settings.LANGUAGE_CODE
    if isinstance(view, str):
        view = import_string(view)
    if (
        not issubclass(view, View)
        or not hasattr(view, "mock_view")
        or not hasattr(view, "model")
    ):
        raise ValueError("Expected a view of type 'CachedDocumentView'.")

    model: Type[Model]
    instance: Model
    model, instance = get_instance_retry(view.model, instance)
    view_instance = view.mock_view(instance)  # Create a fake view

    lock_name = get_document_lock_name(model, instance.pk)
    # A lock is used to prevent multiple workers from creating the same
    # document. Not that the check for ``force`` and the existence of
    # this document is done when the lock has been acquired.
    with redis_lock(lock_name):
        instance.refresh_from_db(fields=(view_instance.model_file_field,))
        file: File = getattr(instance, view_instance.model_file_field)
        if not force and file_exists(file):
            # The file is already cached and does not have to be rebuilt
            logger.debug("Skip file render as 'force' is set to 'False'.")
            return
        with translation.override(language):
            document_template = render_to_string(
                view_instance.get_template_names(),
                context=view_instance.get_context_data(),
                using=view_instance.template_engine,
                # The template engine choice will avoid issues where
                # 'request' is not defined.
            )
        render_document_to_model(
            document_template,
            view_instance.get_internal_filename(),
            view_instance.model,
            view_instance.model_file_field,
            instance,
        )


@shared_task
def render_document_to_model(
    template: str,
    filename: str,
    model: Union[str, Type[Model]],
    model_file_field: str,
    instance: Union[Model, int],
):
    """Render a document to model instance

    This function will create the document (provided by the HTML string
    template) and apply it to the provided model instance.

    :param template: HTML template for the WeasyPrint document.
    :param filename: File name used in the model's file field.
    :param model: Model, like :class:`gcampus.core.models.Measurement`.
    :param model_file_field: String name of the field which holds the
        file.
    :param instance: Either a primary key or an acutal instance of the
        model.
    """
    model, instance = get_instance_retry(model, instance)
    document = render_document_from_html(template)
    filelike_obj: BytesIO
    with as_bytes_io(document) as filelike_obj:
        # Makes sure the memory (buffer) is released after saving the
        # file.
        setattr(instance, model_file_field, File(filelike_obj, name=filename))
        instance.save(update_fields=(model_file_field,))


def get_instance_retry(
    model: Union[str, Type[Model]],
    instance: Union[Model, int],
    max_retry: int = 5,
    retry_delay: int = 5,
) -> Tuple[Type[Model], Model]:
    if isinstance(model, str):
        _model = import_string(model)
        if not issubclass(_model, Model):  # noqa
            raise ValueError(f"'{model}' is not a valid model")
        model: Type[Model] = _model

    if isinstance(instance, model):
        return model, instance

    counter = 0
    while not isinstance(instance, model) and counter <= max_retry:
        counter += 1
        try:
            model_instance: model = model.objects.get(pk=instance)
            return model, model_instance
        except model.DoesNotExist:
            # Do not handle exception
            time.sleep(retry_delay)

    raise model.DoesNotExist(f"Unable to find {model} with 'pk={instance}'")


@shared_task
def document_cleanup():
    """Document cleanup and maintenance task.

    This task will check for broken links between the database and the
    storage backend for media files.
    If a media file is found in the storage backend but no related
    document is found in the database (orphaned file), it is deleted
    from the storage backend.
    The reverse is also applicable: If a file specified in the database
    is not found in the storage backend, the reference is removed from
    the database.

    Note: Only :class:`django.core.files.storage.FileSystemStorage` is
    supported for orphaned files.
    """
    table_columns: list[tuple[Manager, str]] = [
        (Measurement.all_objects, "document"),
        (Course.objects, "overview_document"),
    ]
    for manager, file_field in table_columns:
        _cleanup_database_reference(manager, file_field)
    _cleanup_orphaned_files(table_columns)


def _cleanup_orphaned_files(
    table_columns: list[tuple[Manager, str]], storage: Storage = default_storage
):
    """Cleanup orphaned files.

    Iterate over all files in the file storage backend and check all
    provided managers with their respective file field for references
    to the current file.

    If a file is not referenced by any of the database tables, it is
    being deleted.

    This function only uses I/O functions provided by the file storage
    backend and can thus be used with any storage backend.

    Example usage:

        # Find files that are not referenced by 'Person.picture'
        # where 'Person' is a model and 'picture' is the associated
        # file field.
        _cleanup_orphaned_files([(Person.objects, "picture")]

    :param table_columns: List of tuples with a
        :class:`django.db.models.Manager` and its associated file field.
    :param storage: Optional storage backend.
    """
    for file in get_files(storage):
        if any(
            manager.only(file_field).filter(**{file_field: file}).exists()
            for manager, file_field in table_columns
        ):
            # The file is referenced by at least one database file
            # field, do not delete the file.
            continue
        else:
            storage.delete(file)


def _cleanup_database_reference(manager: Manager, field: str):
    """Cleanup database references to deleted files.

    For a given manager (e.g. ``Model.objects``), find all instances
    that have a file set in their ``field`` column. If the file does
    not exist, the reference is removed at a final step with a single
    ``update`` call.

    :param manager: Django model manager for the table.
    :param field: Column name of the file field.
    """
    # Query for rows where the file field is not set
    empty_file_query: Q = Q(**{f"{field}__isnull": True}) | Q(**{field: ""})
    # List of primary keys that should be reset
    reset_pks: list = []
    # Get all rows that have the file field column set
    for instance in manager.only("pk", field).exclude(empty_file_query):
        file: FieldFile | None = getattr(instance, field, None)
        if not file_exists(file):
            reset_pks.append(instance.pk)
    if reset_pks:
        manager.filter(pk__in=reset_pks).update(**{field: None})
