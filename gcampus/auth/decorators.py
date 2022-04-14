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

from functools import wraps
from typing import Union, List, Optional

from django.contrib.sessions.exceptions import SuspiciousSession
from django.http import HttpRequest

from gcampus.auth import session
from gcampus.auth.exceptions import (
    UnauthenticatedError,
    TokenPermissionError,
    TokenEmptyError,
)
from gcampus.auth.models.token import TokenType, BaseToken
from gcampus.core.models.util import EMPTY


def require_token_type(token_type: Union[TokenType, List[TokenType]]):
    if isinstance(token_type, str):
        token_type = [token_type]

    def decorator(f):
        @wraps(f)
        def wrapper(request: HttpRequest, *args, **kwargs):
            if not session.is_authenticated(request):
                raise UnauthenticatedError()
            token: Optional[BaseToken] = request.token
            if not token:
                raise SuspiciousSession()
            request_token_type = session.get_token_type(request)
            if request_token_type not in token_type or not token.is_active:
                raise TokenPermissionError()
            return f(request, *args, **kwargs)

        return wrapper

    return decorator


require_access_key = require_token_type([TokenType.access_key])
require_course_token = require_token_type([TokenType.course_token])
require_any_token = require_token_type([TokenType.access_key, TokenType.course_token])
