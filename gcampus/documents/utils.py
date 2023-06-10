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

from pathlib import Path

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest


def _mock_get_response():
    return "Response"


def mock_request() -> HttpRequest:
    request = HttpRequest()
    middleware = SessionMiddleware(_mock_get_response)
    middleware.process_request(request)
    request.session.save()
    request.token = None
    return request
