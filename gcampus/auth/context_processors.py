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

from django.conf import settings
from django.http import HttpRequest

from gcampus.auth.models.token import TokenType
from gcampus.auth import session


def auth(request: HttpRequest) -> dict:
    return {
        "authenticated": session.is_authenticated(request),
        "user_token_instance": request.token,
        "user_token": session.get_token(request),
        "user_token_type": session.get_token_type(request),
        "user_token_name": session.get_token_name(request),
        "user_token_is_access_key": (
            session.get_token_type(request) is TokenType.access_key
        ),
        "user_token_is_course_token": (
            session.get_token_type(request) is TokenType.course_token
        ),
        "email_confirmation_timeout": settings.EMAIL_CONFIRMATION_TIMEOUT.days,
    }
