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

from functools import wraps
from typing import Optional

from django.contrib.sessions.exceptions import SuspiciousSession
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from gcampus.auth import session
from gcampus.auth.exceptions import (
    TokenEditPermissionError,
    TokenCreatePermissionError,
    UnauthenticatedError,
)
from gcampus.auth.models import BaseToken
from gcampus.core.models import Measurement


def require_permission_create_measurement(f):
    @wraps(f)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if not session.is_authenticated(request):
            # Handle unauthenticated users.
            # This assumes that all unauthenticated users do not have
            # the permission to create a measurement.
            raise UnauthenticatedError()
        token: Optional[BaseToken] = request.token
        if not token:
            raise SuspiciousSession(
                "Token user is authenticated but 'request.token' is 'None'."
            )
        if not token.has_perm("gcampuscore.add_measurement"):
            raise TokenCreatePermissionError()
        return f(request, *args, **kwargs)

    return wrapper


def require_permission_edit_measurement(f):
    @wraps(f)
    def wrapper(request: HttpRequest, pk: int, *args, **kwargs):
        if not session.is_authenticated(request):
            # Handle unauthenticated users.
            # This assumes that all unauthenticated users do not have
            # the permission to edit a measurement.
            raise UnauthenticatedError()
        token: Optional[BaseToken] = request.token
        if not token:
            raise SuspiciousSession(
                "Token user is authenticated but 'request.token' is 'None'."
            )
        measurement: Measurement = get_object_or_404(Measurement, id=pk)
        if not token.has_perm("gcampuscore.change_measurement", obj=measurement):
            raise TokenEditPermissionError()
        return f(request, pk, *args, **kwargs)

    return wrapper
