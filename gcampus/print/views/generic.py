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
from django.utils.text import get_valid_filename
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin

from gcampus.print.document import render_document, as_bytes_io

__all__ = [
    "DocumentResponse",
    "DocumentView",
    "FileNameMixin",
    "SingleObjectDocumentView",
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
