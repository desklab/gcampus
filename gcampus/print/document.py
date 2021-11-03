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

__all__ = ["render", "as_bytes_io", "as_response", "as_file"]

import pathlib
from io import BytesIO
from pathlib import Path
from typing import Union
from typing import Optional

from django.http import StreamingHttpResponse
from django.template.loader import render_to_string
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest

from weasyprint import HTML, Document

from gcampus.print.static import url_fetcher


STATIC_FILES_PATH = Path(__file__).resolve().parent / "static"


def render(document: str, context: Optional[dict] = None) -> Document:
    request = HttpRequest()
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    document_str = render_to_string(
        f"gcampusprint/documents/{document}.html", 
        context=context,
        request=request,
    )
    html = HTML(string=document_str, url_fetcher=url_fetcher)
    return html.render()


def as_bytes_io(document: Document, **kwargs) -> BytesIO:
    filelike_obj = BytesIO()
    document.write_pdf(target=filelike_obj, **kwargs)
    return filelike_obj


def as_response(
    document: Document,
    filename: str,
    content_type: str = "application/pdf",
) -> StreamingHttpResponse:
    filelike_obj: BytesIO = as_bytes_io(document)
    # Jump to the end of the file-like object
    filelike_obj.seek(0, 2)
    # File position corresponds to the file size
    content_size = filelike_obj.tell()
    # Go back to the beginning
    filelike_obj.seek(0)

    response = StreamingHttpResponse(filelike_obj, content_type=content_type)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    response["Content-Length"] = content_size
    return response


def as_file(document: Document, target: Union[str, pathlib.Path]):
    document.write_pdf(target)
