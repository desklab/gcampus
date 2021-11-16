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

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from gcampus.auth import utils
from gcampus.auth.exceptions import (
    TOKEN_CREATE_PERMISSION_ERROR,
    TOKEN_EDIT_PERMISSION_ERROR
)
from gcampus.auth.models.token import (
    can_token_create_measurement,
    can_token_edit_measurement
)
from gcampus.core.models import Measurement


def require_permission_create_measurement(f):
    @wraps(f)
    def wrapper(request: HttpRequest, *args, **kwargs):
        token = utils.get_token(request)
        token_type = utils.get_token_type(request)
        if not can_token_create_measurement(token, token_type=token_type):
            raise PermissionDenied(TOKEN_CREATE_PERMISSION_ERROR)
        return f(request, *args, **kwargs)
    return wrapper


def require_permission_edit_measurement(f):
    @wraps(f)
    def wrapper(request: HttpRequest, pk: int, *args, **kwargs):
        token = utils.get_token(request)
        token_type = utils.get_token_type(request)
        measurement: Measurement = get_object_or_404(Measurement, id=pk)
        if not can_token_edit_measurement(token, measurement, token_type=token_type):
            raise PermissionDenied(TOKEN_EDIT_PERMISSION_ERROR)
        return f(request, pk, *args, **kwargs)
    return wrapper
