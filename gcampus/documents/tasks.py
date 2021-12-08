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

from pydoc import locate
from typing import Type, Optional, Union

from celery import shared_task
from django.core.files import File
from django.db.models import Model
from django.views import View
from weasyprint import HTML

from gcampus.documents.document import as_bytes_io, render_document_template
from gcampus.documents.utils import url_fetcher


@shared_task
def render_cached_document_view(
    view: Union[str, Type[View]],
    instance: Optional[Model] = None,
    instance_pk: Optional[int] = None,
    force: bool = True
):
    """Render Cached Document View

    Task to render the document for a given :class:`CachedDocumentView`
    and its instance. The document will be rendered and saved to the
    instance's ``model_file_field``.

    To make this work, a fake mock view will be created alongside a mock
    request.

    :param view: Subclass of :class:`CachedDocumentView`.
    :param instance: Optional model instance. If no instance is
        provided, the primary key has to be passed using
        ``instance_pk``.
    :param instance_pk: Optional primary key for the instance. Has to
        be set if ``instance`` is not set.
    :param force: Force document rebuild even if document is already
        saved in the model.
    """
    if isinstance(view, str):
        view = locate(view)
    if not issubclass(view, View) or not hasattr(view, "mock_view"):
        raise ValueError("Expected a view of type 'CachedDocumentView'.")
    view_instance = view.mock_view(
        instance=instance, instance_pk=instance_pk
    )  # Create a fake view
    _instance = view_instance.object
    if _instance is None:
        # This should never happen
        raise ValueError("Unable to find an instance")
    if not force and getattr(_instance, view_instance.model_file_field):
        # The file is already cached and does not have to be rebuilt
        return
    document_template = render_document_template(
        view_instance.get_template_names(),
        context=view_instance.get_context_data(),
        request=view_instance.request,
        using=view_instance.template_engine
    )
    render_document_to_model(
        document_template,
        view_instance.get_internal_filename(),
        view_instance.model,
        view_instance.model_file_field,
        instance=_instance,
    )


@shared_task
def render_document_to_model(
    template: str,
    filename: str,
    model: Union[str, Type[Model]],
    model_file_field: str,
    instance: Optional[Model] = None,
    instance_pk: Optional[int] = None,
):
    if isinstance(model, str):
        _model = locate(model)
        if not issubclass(_model, Model):  # noqa
            raise ValueError(f"'{model}' is not a valid model")
        model: Type[Model] = _model
    if instance is None:
        if instance_pk is None:
            raise ValueError("One of 'instance' and 'instance_pk' has to be set")
        instance: Model = model.objects.get(pk=instance_pk)
    html = HTML(string=template, url_fetcher=url_fetcher)
    document = html.render()
    filelike_obj = as_bytes_io(document)
    setattr(instance, model_file_field, File(filelike_obj, name=filename))
    instance.save(update_fields=(model_file_field,))
