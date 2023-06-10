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

__all__ = [
    "render_document_template",
    "render_document",
    "as_bytes_io",
    "as_file",
]

import mimetypes
import os
import pathlib
import posixpath
from io import BytesIO
from typing import Optional, List, Union
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpRequest
from django.template.loader import render_to_string
from weasyprint import HTML, Document
from weasyprint.urls import URLFetchingError, default_url_fetcher

from gcampus.core import get_base_url
from gcampus.documents.utils import mock_request


def url_fetcher(url: str, **kwargs):
    try:
        o = urlsplit(url)
    except ValueError:
        return default_url_fetcher(url, **kwargs)
    if o.netloc == settings.PRIMARY_HOST and o.path.startswith(settings.STATIC_URL):
        path = os.path.relpath(o.path, settings.STATIC_URL)
        normalized_path = posixpath.normpath(path).lstrip("/")
        mime_type, encoding = mimetypes.guess_type(path, strict=True)
        if getattr(settings, "AWS_STATIC_USE_STATIC_URL", False):
            from django.contrib.staticfiles.storage import staticfiles_storage

            file_obj = staticfiles_storage.open(normalized_path)
        else:
            absolute_path = finders.find(normalized_path)
            if not absolute_path:
                raise FileNotFoundError()
            if not os.path.isfile(absolute_path):
                raise URLFetchingError(
                    f"File '{url}' (resolved to '{absolute_path}') not found!"
                )
            file_obj = open(absolute_path, "rb")
        return {
            "mime_type": mime_type,
            "encoding": encoding,
            "file_obj": file_obj,
        }
    else:
        return default_url_fetcher(url, **kwargs)


def render_document_template(
    template: Union[str, List[str]],
    context: Optional[dict] = None,
    request: Optional[HttpRequest] = None,
    using=None,
) -> str:
    # Add dummy request to enable context processors.
    # Context processors will not be run when no request is provided,
    # even if they might not require a request.
    if request is None:
        request = mock_request()
    return render_to_string(template, context=context, request=request, using=using)


def render_document(
    template: Union[str, List[str]],
    context: Optional[dict] = None,
    request: Optional[HttpRequest] = None,
    using=None,
) -> Document:
    document_str = render_document_template(template, context, request, using)
    html = HTML(string=document_str, url_fetcher=url_fetcher, base_url=get_base_url())
    return html.render()


def as_bytes_io(document: Document, **kwargs) -> BytesIO:
    filelike_obj = BytesIO()
    document.write_pdf(target=filelike_obj, **kwargs)
    return filelike_obj


def as_file(document: Document, target: Union[str, pathlib.Path]):
    document.write_pdf(target)
