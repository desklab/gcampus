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

from django import template
from django.http import HttpRequest
from django.template import Context

register = template.Library()


def _is_current_view(request: HttpRequest, view_name: str) -> bool:
    try:
        current_view: str = request.resolver_match.view_name
    except AttributeError:
        return False
    return current_view == view_name


@register.simple_tag(takes_context=True)
def active_link(context: Context, view_name: str, yesno: str = "active,") -> str:
    request: HttpRequest = context["request"]
    yes, no = yesno.split(",")
    if _is_current_view(request, view_name):
        return yes
    else:
        return no


@register.simple_tag(takes_context=True)
def aria_current(context: Context, view_name: str) -> str:
    request: HttpRequest = context["request"]
    if _is_current_view(request, view_name):
        return 'aria-current="page"'
    else:
        return ""
