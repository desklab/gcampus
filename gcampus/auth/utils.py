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

from typing import Optional

from django.http import HttpRequest

TOKEN_STORE = "gcampusauth_token"
AUTHENTICATION_BOOLEAN = "gcampusauth_authenticated"


def get_token(request: HttpRequest, default: str = None) -> Optional[str]:
    if TOKEN_STORE in request.session:
        return request.session[TOKEN_STORE].get("token", default)
    return default


def get_token_type(request: HttpRequest, default: str = None) -> Optional[str]:
    if TOKEN_STORE in request.session:
        return request.session[TOKEN_STORE].get("token_type", default)
    return default


def set_token(request: HttpRequest, token: str, token_type: str, token_name):
    request.session[TOKEN_STORE] = {
        "token": token,
        "token_type": token_type,
        "token_name": token_name,
    }
    request.session[AUTHENTICATION_BOOLEAN] = True


def logout(request: HttpRequest):
    request.session[TOKEN_STORE] = {}
    request.session[AUTHENTICATION_BOOLEAN] = False
