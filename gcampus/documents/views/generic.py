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

from io import BytesIO
from typing import Optional

from django.http import StreamingHttpResponse, HttpRequest
from django.shortcuts import redirect
from django.utils.text import get_valid_filename
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin

from gcampus.core.models.util import EMPTY
from gcampus.documents.document import render_document, as_bytes_io

__all__ = [
    "DocumentResponse",
    "DocumentView",
    "FileNameMixin",
    "SingleObjectDocumentView",
    "CachedDocumentView",
]


class DocumentResponse(StreamingHttpResponse):
    def __init__(
        self,
        request: HttpRequest,
        template,
        context=None,
        content_type=None,
        filename=None,
        using=None,
        headers=None,
    ):
        document = render_document(
            template, context=context, request=request, using=using
        )
        filelike_obj: BytesIO = as_bytes_io(document)
        # Jump to the end of the file-like object
        filelike_obj.seek(0, 2)
        # File position corresponds to the file size
        content_size = filelike_obj.tell()
        # Go back to the beginning
        filelike_obj.seek(0)

        if headers is None:
            headers = {}
        if "Content-Disposition" not in headers:
            headers["Content-Disposition"] = f"attachment; filename={filename}"
        if "Content-Length" not in headers:
            headers["Content-Length"] = content_size
        super().__init__(filelike_obj, content_type=content_type, headers=headers)


class FileNameMixin:
    filename: Optional[str] = None

    def get_filename(self) -> Optional[str]:
        return self.filename


class DocumentView(FileNameMixin, TemplateView):
    content_type = "application/pdf"
    response_class = DocumentResponse

    def render_to_response(self, context, **response_kwargs):
        response_kwargs["filename"] = get_valid_filename(self.get_filename())
        return super(DocumentView, self).render_to_response(context, **response_kwargs)


class SingleObjectDocumentView(SingleObjectMixin, DocumentView):
    def __init__(self, *args, **kwargs):
        self.object = None
        super(SingleObjectDocumentView, self).__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class CachedDocumentView(SingleObjectDocumentView):
    model_file_field: Optional[str] = None

    @classmethod
    def as_view(cls, **initkwargs):
        if not isinstance(cls.model_file_field, str):
            raise ValueError(
                f"Invalid configuration of '{cls.__name__}': Expected field "
                f"'model_file_field' to be a string but got "
                f"'{type(cls.model_file_field)}'."
            )
        return super(CachedDocumentView, cls).as_view(**initkwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not hasattr(self.object, self.model_file_field):
            raise ValueError(
                f"Field '{self.model_file_field}' not found in model "
                f"'{self.model.__name__}'."
            )
        file = getattr(self.object, self.model_file_field)
        if file is not None and file.url not in EMPTY:
            return redirect(file.url)
        else:
            context = self.get_context_data(object=self.object)
