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
from typing import Type, Union, Tuple

from celery import shared_task
from django.conf import settings
from django.core.files import File
from django.db.models import Model
from django.utils import translation
from django.utils.module_loading import import_string
from django.views import View
from weasyprint import HTML

from gcampus.documents.document import as_bytes_io, render_document_template
from gcampus.documents.utils import url_fetcher
from gcampus.tasks.lock import redis_lock

logger = logging.getLogger("gcampus.documents.tasks")


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
    translation.activate(language)
    if isinstance(view, str):
        view = import_string(view)
    if (
        not issubclass(view, View)
        or not hasattr(view, "mock_view")
        or not hasattr(view, "model")
    ):
        raise ValueError("Expected a view of type 'CachedDocumentView'.")

    model, _instance = get_instance_retry(view.model, instance)
    view_instance = view.mock_view(_instance)  # Create a fake view

    lock_name = f"render_cached_document_view_{view.__name__}_{_instance.pk}"
    # A lock is used to prevent multiple workers from creating the same
    # document. Not that the check for ``force`` and the existence of
    # this document is done when the lock has been acquired.
    with redis_lock(lock_name):
        _instance.refresh_from_db(fields=(view_instance.model_file_field,))
        if not force and getattr(_instance, view_instance.model_file_field):
            # The file is already cached and does not have to be rebuilt
            logger.debug("Skip file render as 'force' is set to 'False'.")
            return
        document_template = render_document_template(
            view_instance.get_template_names(),
            context=view_instance.get_context_data(),
            request=view_instance.request,
            using=view_instance.template_engine,
        )
        render_document_to_model(
            document_template,
            view_instance.get_internal_filename(),
            view_instance.model,
            view_instance.model_file_field,
            _instance,
            language,
        )


@shared_task
def render_document_to_model(
    template: str,
    filename: str,
    model: Union[str, Type[Model]],
    model_file_field: str,
    instance: Union[Model, int],
    language: str,
):
    translation.activate(language)
    model, instance = get_instance_retry(model, instance)
    html = HTML(string=template, url_fetcher=url_fetcher)
    document = html.render()
    filelike_obj = as_bytes_io(document)
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
