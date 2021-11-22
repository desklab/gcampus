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

# __all__ = ["render_document", "as_bytes_io", "as_file"]
import mimetypes
import os
import pathlib
import posixpath
from io import BytesIO
from pathlib import Path
from typing import Optional
from typing import Union

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.staticfiles import finders
from django.http import HttpRequest
from django.template.loader import render_to_string
from weasyprint import HTML, Document
from weasyprint.urls import URLFetchingError, default_url_fetcher

STATIC_FILES_PATH = Path(__file__).resolve().parent / "static"
URI_IDENTIFIER = "gcampusprint"


def render_document(
    template: str,
    context: Optional[dict] = None,
    request: Optional[HttpRequest] = None,
    using=None,
) -> Document:
    # Add dummy request to enable context processors
    if request is None:
        request = HttpRequest()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    document_str = render_to_string(
        template, context=context, request=request, using=using
    )
    html = HTML(string=document_str, url_fetcher=url_fetcher)
    return html.render()


def as_bytes_io(document: Document, **kwargs) -> BytesIO:
    filelike_obj = BytesIO()
    document.write_pdf(target=filelike_obj, **kwargs)
    return filelike_obj


def as_file(document: Document, target: Union[str, pathlib.Path]):
    document.write_pdf(target)


def url_fetcher(url: str, **kwargs):
    if url.startswith(f"{URI_IDENTIFIER}:"):
        # Remove the URI identifier only used to trigger the URL fetcher
        url = url[len(URI_IDENTIFIER) + 1 :]
    if url.startswith(settings.STATIC_URL):
        path = url.replace(settings.STATIC_URL, "", 1)
        normalized_path = posixpath.normpath(path).lstrip("/")
        absolute_path = finders.find(normalized_path)
        if not absolute_path:
            raise FileNotFoundError()
        if not os.path.isfile(absolute_path):
            raise URLFetchingError(
                f"File '{url}' (resolved to '{absolute_path}') not found!"
            )
        mime_type, encoding = mimetypes.guess_type(absolute_path, strict=True)
        return {
            "mime_type": mime_type,
            "encoding": encoding,
            "file_obj": open(absolute_path, "rb"),
        }
    else:
        return default_url_fetcher(url, **kwargs)
