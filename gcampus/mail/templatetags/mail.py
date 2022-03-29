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

import posixpath
from os import path

from django import template
from django.contrib.staticfiles import finders

register = template.Library()


@register.simple_tag
def include_static(static_path: str) -> str:
    normalized_path = posixpath.normpath(static_path).lstrip("/")
    absolute_path = finders.find(normalized_path)
    if not absolute_path:
        raise FileNotFoundError()
    if not path.isfile(absolute_path):
        raise RuntimeError(
            f"'finders.find' returned a path but '{absolute_path}' is not a file"
        )
    with open(absolute_path, "r") as f:
        content = f.read()
    return content
