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

__all__ = [
    "RegisterFormView",
    "AccessKeyFormView",
    "CourseTokenFormView",
    "AccessKeyDeactivationView",
    "logout",
    "permission_denied_error_handler",
    "CourseUpdateView",
    "EmailConfirmationView",
    "AccessKeyCreateView",
]

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest
from django.views.defaults import permission_denied, ERROR_403_TEMPLATE_NAME

from gcampus.auth.exceptions import (
    UnauthenticatedError,
    TokenCreatePermissionError,
    TokenEditPermissionError,
    TokenPermissionError,
    EmailVerificationExpired,
)
from gcampus.auth.views.course import (
    CourseUpdateView,
    AccessKeyCreateView,
    EmailConfirmationView,
    AccessKeyDeactivationView,
)
from gcampus.auth.views.register import RegisterFormView
from gcampus.auth.views.token import AccessKeyFormView, CourseTokenFormView, logout


def permission_denied_error_handler(
    request: HttpRequest,
    exception: PermissionDenied,
    template_name: str = ERROR_403_TEMPLATE_NAME,
) -> HttpResponse:
    if isinstance(exception, UnauthenticatedError):
        template_name = "gcampusauth/error/403_unauthenticated.html"
    elif isinstance(exception, TokenCreatePermissionError):
        template_name = "gcampusauth/error/403_create_permission.html"
    elif isinstance(exception, TokenEditPermissionError):
        template_name = "gcampusauth/error/403_edit_permission.html"
    elif isinstance(exception, TokenPermissionError):
        template_name = "gcampusauth/error/403_view_permission.html"
    elif isinstance(exception, EmailVerificationExpired):
        template_name = "gcampusauth/error/403_email_verification_expired.html"
    return permission_denied(request, exception, template_name=template_name)
