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

__all__ = [
    "render_document_template",
    "render_document",
    "as_bytes_io",
    "as_file",
]

import pathlib
from io import BytesIO
from typing import Optional, List
from typing import Union

from django.http import HttpRequest
from django.template.loader import render_to_string
from weasyprint import HTML, Document

from gcampus.documents.utils import mock_request, url_fetcher


def render_document_template(
    template: Union[str, List[str]],
    context: Optional[dict] = None,
    request: Optional[HttpRequest] = None,
    using=None,
) -> str:
    # Add dummy request to enable context processors
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
    html = HTML(string=document_str, url_fetcher=url_fetcher)
    return html.render()


def as_bytes_io(document: Document, **kwargs) -> BytesIO:
    filelike_obj = BytesIO()
    document.write_pdf(target=filelike_obj, **kwargs)
    return filelike_obj


def as_file(document: Document, target: Union[str, pathlib.Path]):
    document.write_pdf(target)

