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

from django import template
from django.http import HttpRequest
from django.template import Context
from django.urls import reverse
from django.utils.encoding import iri_to_uri
from django.utils.http import urlencode

from gcampus.auth import session
from gcampus.auth.models.token import TokenType

register = template.Library()


@register.simple_tag(takes_context=True)
def request_params(context: Context) -> str:
    request: HttpRequest = context["request"]
    query_string = request.META.get("QUERY_STRING", "")
    return ("?" + iri_to_uri(query_string)) if query_string else ""


@register.simple_tag(takes_context=True)
def filter_params(context: Context, **kwargs) -> str:
    request: HttpRequest = context["request"]
    kwargs.setdefault("other_courses", True)
    if session.is_authenticated(request):
        if session.get_token_type(request) is TokenType.access_key:
            kwargs.setdefault("same_access_key", True)
        kwargs.setdefault("same_course", True)
    return urlencode(kwargs)


@register.simple_tag(takes_context=True)
def measurements_url(context: Context, **kwargs) -> str:
    return "?".join(
        [reverse("gcampuscore:measurements"), filter_params(context, **kwargs)]
    )
