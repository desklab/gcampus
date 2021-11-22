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
import os

from django import template
from django.templatetags.static import do_static, StaticNode

from gcampus.print.document import URI_IDENTIFIER


register = template.Library()


class PrintStaticNode(StaticNode):
    def url(self, context):
        path = self.path.resolve(context)
        return f"{URI_IDENTIFIER}:{self.handle_simple(path)}"


@register.tag
def print_static(parser, token):
    if os.environ.get("USE_S3_STORAGE", False):
        return do_static(parser, token)
    else:
        return PrintStaticNode.handle_token(parser, token)
