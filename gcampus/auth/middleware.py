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

__all__ = ["TokenAuthMiddleware"]

from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from gcampus.auth import session
from gcampus.auth.models.token import BaseToken


def get_token_instance(request: HttpRequest) -> Optional[BaseToken]:
    if not hasattr(request, "_cached_token"):
        try:
            request._cached_token = session.get_token_instance(request)
        except ValueError:
            request._cached_token = None  # Also cache if no user is set
    return request._cached_token  # noqa


class TokenAuthMiddleware(MiddlewareMixin):
    """The token authentication middleware handles the ``request.token``
    attribute and fetches the token instance (of type
    :class:`gcampus.auth.models.BaseToken`) from the database.
    """

    def process_request(self, request: HttpRequest):
        if not hasattr(request, "session"):
            raise ImproperlyConfigured(
                "The token authentication middleware requires session "
                "middleware to be installed. Edit your MIDDLEWARE setting to "
                "insert "
                "'django.contrib.sessions.middleware.SessionMiddleware' before "
                "'gcampus.auth.middleware.TokenAuthMiddleware'."
            )
        # Necessary to avoid issues when ``get_token_instance`` fails.
        request.token = None
        request.token = SimpleLazyObject(lambda: get_token_instance(request))
