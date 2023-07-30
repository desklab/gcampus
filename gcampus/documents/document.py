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
    "render_document_from_html",
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
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string
from weasyprint import HTML, Document
from weasyprint.urls import default_url_fetcher

from gcampus.core import get_base_url

DOCUMENT_TEMPLATE_ENGINE: str = "document"


def url_fetcher(url: str, **kwargs):
    try:
        o = urlsplit(url)
    except ValueError:
        return default_url_fetcher(url, **kwargs)
    if o.netloc == settings.PRIMARY_HOST and o.path.startswith(settings.STATIC_URL):
        path = os.path.relpath(o.path, settings.STATIC_URL)
        normalized_path = posixpath.normpath(path).lstrip("/")
        mime_type, encoding = mimetypes.guess_type(path, strict=True)
        absolute_path = finders.find(normalized_path)
        try:
            if not absolute_path:
                raise FileNotFoundError()
            if not os.path.isfile(absolute_path) or not os.path.exists(absolute_path):
                raise FileNotFoundError(
                    f"File '{url}' (resolved to '{absolute_path}') not found!"
                )
            file_obj = open(absolute_path, "rb")
        except FileNotFoundError:
            file_obj = staticfiles_storage.open(normalized_path, mode="rb")
        return {
            "mime_type": mime_type,
            "encoding": encoding,
            "file_obj": file_obj,
        }
    else:
        return default_url_fetcher(url, **kwargs)


def render_document(
    template: Union[str, List[str]],
    context: Optional[dict] = None,
    using=DOCUMENT_TEMPLATE_ENGINE,
) -> Document:
    document_str = render_to_string(template, context=context, using=using)
    return render_document_from_html(document_str)


def render_document_from_html(html: str) -> Document:
    """Render a document from a provided HTML string.

    Applies all the required parameters like the ``url_fetcher``
    and ``base_url`` to render the WeasyPrint document.

    :param html: String HTML, e.g. rendered from a template using
        :func:`django.template.loader.render_to_string`.
    :returns: A rendered :class:`weasyprint.Document` instance.
    """
    return HTML(string=html, url_fetcher=url_fetcher, base_url=get_base_url()).render()


def as_bytes_io(document: Document, **kwargs) -> BytesIO:
    filelike_obj = BytesIO()
    document.write_pdf(target=filelike_obj, **kwargs)
    return filelike_obj


def as_file(document: Document, target: Union[str, pathlib.Path]):
    document.write_pdf(target)
