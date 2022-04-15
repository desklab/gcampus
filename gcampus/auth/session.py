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
from datetime import datetime
from typing import Optional

from django.contrib import messages
from django.contrib.sessions.exceptions import SuspiciousSession
from django.http import HttpRequest

from gcampus.auth.exceptions import ACCESS_KEY_DEACTIVATED_ERROR
from gcampus.auth.models.token import TokenType, BaseToken, AccessKey, CourseToken
from gcampus.auth.signals import token_user_logged_in

TOKEN_STORE = "gcampusauth_token"
AUTHENTICATION_BOOLEAN = "gcampusauth_authenticated"

logger = logging.getLogger("gcampus.auth.session")


def _get_token_pk(request: HttpRequest, default: str = None):
    if TOKEN_STORE in request.session:
        return request.session[TOKEN_STORE].get("token_pk", default)
    return default


def get_token(request: HttpRequest, default: str = None) -> Optional[str]:
    token_instance: BaseToken = request.token
    if not token_instance:
        return default
    else:
        return token_instance.token


def get_token_type(request: HttpRequest, default: str = None) -> Optional[TokenType]:
    if TOKEN_STORE in request.session:
        token_type = request.session[TOKEN_STORE].get("token_type", None)
        if token_type is None:
            return default
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
    token_instance: BaseToken = request.token
    if not token_instance:
        return default
    else:
        return token_instance.course.name


def is_authenticated(request: HttpRequest) -> bool:
    return request.session.get(AUTHENTICATION_BOOLEAN, False)


def set_token(request: HttpRequest, token: BaseToken, token_type: TokenType):
    logout(request)
    _set_token_session(request.session, token, token_type)
    token_user_logged_in.send(sender=token, instance=token, request=request)


def _set_token_session(session, token: BaseToken, token_type: TokenType):
    session[TOKEN_STORE] = {
        "token_pk": token.pk,
        # the 'value' attribute gives a string representation of the
        # token type
        "token_type": token_type.value,
    }
    session[AUTHENTICATION_BOOLEAN] = True


def get_token_instance(request: HttpRequest) -> Optional[BaseToken]:
    """

    :raises ValueError: If no token user is authenticated.
    :raises SuspiciousSession: Authenticated but session is invalid.
    """
    if not is_authenticated(request):
        raise ValueError("Token user not authenticated.")
    token_pk: Optional[str] = _get_token_pk(request, default=None)
    if token_pk is None:
        logout(request)  # clean session
        raise SuspiciousSession(
            "Invalid session: Token user is authenticated but no token is set."
        )
    token_type = get_token_type(request, default=None)
    if token_type not in TokenType:
        logout(request)  # clean session
        raise SuspiciousSession(
            "Invalid session: Token user is authenticated but token type is invalid."
        )
    instance: BaseToken
    if token_type is TokenType.access_key:
        try:
            instance = AccessKey.objects.select_related("course").get(pk=token_pk)
        except AccessKey.DoesNotExist:
            logout(request)
            raise SuspiciousSession(
                f"It seems like the access key with 'pk={token_pk}' has been deleted."
            )
    elif token_type is TokenType.course_token:
        try:
            instance = CourseToken.objects.select_related("course").get(pk=token_pk)
        except CourseToken.DoesNotExist:
            logout(request)
            raise SuspiciousSession(
                f"It seems like the course token with 'pk={token_pk}' has been deleted."
            )
    else:
        # There is no other token type.
        raise NotImplementedError()

    if not instance.is_active:
        messages.error(request, ACCESS_KEY_DEACTIVATED_ERROR)
        logout(request)
        return None

    return instance


def logout(request: HttpRequest):
    request._cached_token = None
    request.session[TOKEN_STORE] = {}
    request.session[AUTHENTICATION_BOOLEAN] = False
