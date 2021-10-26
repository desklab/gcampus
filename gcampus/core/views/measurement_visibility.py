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
from django.contrib import messages
from django.core.exceptions import PermissionDenied, BadRequest
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext
from django.views.decorators.http import require_POST

from gcampus.auth import exceptions
from gcampus.auth.models.token import COURSE_TOKEN_TYPE
from gcampus.auth.utils import (
    is_authenticated,
    get_token,
    get_token_type,
)
from gcampus.core.models import Measurement


def _check_general_permission(request: HttpRequest):
    if not is_authenticated(request):
        # User is not authenticated
        raise PermissionDenied()
    token = get_token(request)
    if token is None:
        raise PermissionDenied(exceptions.TOKEN_EMPTY_ERROR)
    if not get_token_type(request) == COURSE_TOKEN_TYPE:
        # User does not have the correct token type
        raise PermissionDenied(exceptions.TOKEN_EDIT_PERMISSION_ERROR)
    pk = request.POST.get("measurement", None)
    if pk is None:
        raise BadRequest()


@require_POST
def hide(request):
    _check_general_permission(request)
    token = get_token(request)
    pk = request.POST.get("measurement", None)
    measurement: Measurement = get_object_or_404(Measurement, pk=pk)
    course_token = measurement.token.parent_token

    if course_token.token == token:
        measurement.hidden = True
        measurement.save()
        messages.success(
            request,
            gettext('You successfully hid the measurement "{measurement:s}"').format(
                measurement=str(measurement)
            ),
        )
        return redirect("gcampuscore:measurement_detail", pk=pk)
    else:
        raise PermissionDenied(exceptions.TOKEN_EDIT_PERMISSION_ERROR)


@require_POST
def show(request):
    _check_general_permission(request)
    token = get_token(request)
    pk = request.POST.get("measurement", None)
    measurement: Measurement = get_object_or_404(Measurement, pk=pk)
    course_token = measurement.token.parent_token

    if course_token.token == token:
        measurement.hidden = False
        measurement.save()
        messages.success(
            request,
            gettext(
                'You successfully made the measurement "{measurement:s}" public'
            ).format(measurement=str(measurement)),
        )
        return redirect("gcampuscore:measurement_detail", pk=pk)
    else:
        raise PermissionDenied(exceptions.TOKEN_EDIT_PERMISSION_ERROR)
