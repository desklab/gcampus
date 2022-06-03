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

import mimetypes
import os
import posixpath
from pathlib import Path

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.staticfiles import finders
from django.http import HttpRequest
from weasyprint.urls import URLFetchingError, default_url_fetcher

STATIC_FILES_PATH = Path(__file__).resolve().parent / "static"
URI_IDENTIFIER = "gcampusdocuments"


def _mock_get_response():
    return "Response"


def mock_request() -> HttpRequest:
    request = HttpRequest()
    middleware = SessionMiddleware(_mock_get_response)
    middleware.process_request(request)
    request.session.save()
    request.token = None
    return request


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
