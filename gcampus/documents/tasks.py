#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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

import logging
from pydoc import locate
from typing import Type, Union

from celery import shared_task
from django.core.files import File
from django.db.models import Model
from django.views import View
from django.utils import translation
from weasyprint import HTML

from gcampus.documents.document import as_bytes_io, render_document_template
from gcampus.documents.utils import url_fetcher
from gcampus.tasks.lock import weak_lock_task

logger = logging.getLogger("gcampus.documents.tasks")


@shared_task
@weak_lock_task
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
    translation.activate(language)
    if isinstance(view, str):
        view = locate(view)
    if not issubclass(view, View) or not hasattr(view, "mock_view"):
        raise ValueError("Expected a view of type 'CachedDocumentView'.")
    view_instance = view.mock_view(instance)  # Create a fake view
    _instance: Model = view_instance.object
    if _instance is None:
        # This should never happen
        raise ValueError("Unable to find an instance")
    _instance.refresh_from_db(fields=(view_instance.model_file_field,))
    if not force and getattr(_instance, view_instance.model_file_field):
        # The file is already cached and does not have to be rebuilt
        logger.info("Skip file render as 'force' is set to 'False'.")
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
@weak_lock_task
def render_document_to_model(
    template: str,
    filename: str,
    model: Union[str, Type[Model]],
    model_file_field: str,
    instance: Union[Model, int],
    language: str,
):
    translation.activate(language)
    if isinstance(model, str):
        _model = locate(model)
        if not issubclass(_model, Model):  # noqa
            raise ValueError(f"'{model}' is not a valid model")
        model: Type[Model] = _model
    if not isinstance(instance, Model):
        instance: Model = model.objects.get(pk=instance)
    html = HTML(string=template, url_fetcher=url_fetcher)
    document = html.render()
    filelike_obj = as_bytes_io(document)
    setattr(instance, model_file_field, File(filelike_obj, name=filename))
    instance.save(update_fields=(model_file_field,))
