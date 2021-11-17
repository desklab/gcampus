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
from typing import Union, List

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from gcampus.auth import utils
from gcampus.auth.exceptions import (
    TOKEN_PERMISSION_ERROR, TOKEN_EMPTY_ERROR, UNAUTHENTICATED_ERROR
)
from gcampus.auth.models.token import ACCESS_TOKEN_TYPE, COURSE_TOKEN_TYPE
from gcampus.core.models.util import EMPTY


def require_token_type(token_type: Union[str, List[str]]):
    if isinstance(token_type, str):
        token_type = [token_type]

    def decorator(f):
        @wraps(f)
        def wrapper(request: HttpRequest, *args, **kwargs):
            if not utils.is_authenticated(request):
                raise PermissionDenied(UNAUTHENTICATED_ERROR)
            request_token = utils.get_token(request)
            request_token_type = utils.get_token_type(request)
            if request_token in EMPTY:
                raise PermissionDenied(TOKEN_EMPTY_ERROR)
            if request_token_type not in token_type:
                raise PermissionDenied(TOKEN_PERMISSION_ERROR)
            return f(request, *args, **kwargs)
        return wrapper
    return decorator


require_access_key = require_token_type([ACCESS_TOKEN_TYPE])
require_course_token = require_token_type([COURSE_TOKEN_TYPE])
