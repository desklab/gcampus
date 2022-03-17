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
from django.utils.encoding import iri_to_uri
from django.template import Context

register = template.Library()


@register.simple_tag(takes_context=True)
def request_params(context: Context) -> str:
    request: HttpRequest = context["request"]
    query_string = request.META.get('QUERY_STRING', '')
    return ('?' + iri_to_uri(query_string)) if query_string else ''
