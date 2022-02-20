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
from abc import ABC
from typing import Optional

from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

UNAUTHENTICATED_ERROR = _("This page can only be accessed by authenticated users")
TOKEN_EDIT_PERMISSION_ERROR = _("You are not allowed to edit this measurement")
TOKEN_CREATE_PERMISSION_ERROR = _("You are not allowed to create a measurement")
TOKEN_EMPTY_ERROR = _(
    "You are not authenticated and cannot create or edit a measurement"
)
TOKEN_PERMISSION_ERROR = _("You do not have the permission to access this site")
TOKEN_INVALID_ERROR = _(
    "Provided course token or access key is not valid or does not exist"
)

# Deactivation messages
ACCESS_KEY_DEACTIVATED_ERROR = _(
    "This access key has been deactivated and can no longer be used. "
    "Please contact the responsible teacher for more information."
)
COURSE_TOKEN_DEACTIVATED_ERROR = _(
    "This course token has been deactivated and can no longer be used."
)


class TokenPermissionDenied(PermissionDenied, ABC):
    _default_message = None

    def __init__(self, message: Optional[str] = None):
        if message is not None:
            super().__init__(message)
        else:
            super().__init__(self._default_message)


class UnauthenticatedError(TokenPermissionDenied):
    _default_message = UNAUTHENTICATED_ERROR


class TokenInvalidError(TokenPermissionDenied):
    _default_message = TOKEN_INVALID_ERROR


class TokenEmptyError(TokenPermissionDenied):
    _default_message = TOKEN_EMPTY_ERROR


class TokenPermissionError(TokenPermissionDenied):
    _default_message = TOKEN_PERMISSION_ERROR


class TokenEditPermissionError(TokenPermissionDenied):
    _default_message = TOKEN_EDIT_PERMISSION_ERROR


class TokenCreatePermissionError(TokenPermissionDenied):
    _default_message = TOKEN_CREATE_PERMISSION_ERROR
