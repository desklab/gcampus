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

import logging
from typing import Optional

from django.http import HttpRequest

from gcampus.auth.models.token import TokenType

TOKEN_STORE = "gcampusauth_token"
AUTHENTICATION_BOOLEAN = "gcampusauth_authenticated"

logger = logging.getLogger("gcampus.auth.session")


def get_token(request: HttpRequest, default: str = None) -> Optional[str]:
    if TOKEN_STORE in request.session:
        return request.session[TOKEN_STORE].get("token", default)
    return default


def get_token_type(request: HttpRequest, default: str = None) -> Optional[TokenType]:
    if TOKEN_STORE in request.session:
        token_type = request.session[TOKEN_STORE].get("token_type", default)
        try:
            # get the token type with matching value
            return TokenType(token_type)
        except ValueError:
            logger.warning(
                f"Invalid token type: '{token_type}'. Return default value instead."
            )
            return default
    return default


def get_token_name(request: HttpRequest, default: str = None) -> Optional[str]:
    if TOKEN_STORE in request.session:
        return request.session[TOKEN_STORE].get("token_name", default)
    return default


def is_authenticated(request: HttpRequest) -> bool:
    return request.session.get(AUTHENTICATION_BOOLEAN, False)


def set_token(request: HttpRequest, token: str, token_type: TokenType, token_name):
    set_token_session(request.session, token, token_type, token_name)


def set_token_session(session, token: str, token_type: TokenType, token_name: str):
    session[TOKEN_STORE] = {
        "token": token,
        # the 'value' attribute gives a string representation of the
        # token type
        "token_type": token_type.value,
        "token_name": token_name,
    }
    session[AUTHENTICATION_BOOLEAN] = True


def logout(request: HttpRequest):
    request.session[TOKEN_STORE] = {}
    request.session[AUTHENTICATION_BOOLEAN] = False
