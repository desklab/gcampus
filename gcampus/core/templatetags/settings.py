#  Copyright (C) 2023 desklab gUG (haftungsbeschränkt)
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

from typing import Any

from django import template
from django.conf import settings as django_settings

register = template.Library()


@register.simple_tag
def settings(name: str, default="") -> Any:
    """Get settings from a template.

    Example usage:

        {% settings "DEBUG" %}

    With default value:

        {% settings "SOME_MISSING_SETTING" default="foo" %}

    """
    return getattr(django_settings, name, default)
