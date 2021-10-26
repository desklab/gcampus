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

from django.http import HttpRequest

from gcampus.auth.models.token import ACCESS_TOKEN_TYPE, COURSE_TOKEN_TYPE
from gcampus.auth.utils import (
    is_authenticated,
    get_token,
    get_token_type,
    get_token_name,
)


def auth(request: HttpRequest) -> dict:
    return {
        "authenticated": is_authenticated(request),
        "user_token": get_token(request),
        "user_token_type": get_token_type(request),
        "user_token_name": get_token_name(request),
        "user_token_is_access_key": get_token_type(request) == ACCESS_TOKEN_TYPE,
        "user_token_is_course_token": get_token_type(request) == COURSE_TOKEN_TYPE,
    }
