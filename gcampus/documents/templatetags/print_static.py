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

from gcampus.documents.utils import URI_IDENTIFIER

register = template.Library()


class PrintStaticNode(StaticNode):
    def url(self, context):
        path = self.path.resolve(context)
        return f"{URI_IDENTIFIER}:{self.handle_simple(path)}"


@register.tag
def print_static(parser, token):
    if os.environ.get("USE_S3_STORAGE", False):
        # When using S3 storage, the URL to the static content will
        # start with 'http(s)' and will thereby trigger WeasyPrint's
        # 'fetch' function, calling the custom 'url_fetcher'.
        return do_static(parser, token)
    else:
        # When using default static file storage, the URL will just be
        # a file path. This will not call the 'url_fetcher' function.
        # Thus, a custom URI protocol ('URI_IDENTIFIER') is being
        # prepended.
        return PrintStaticNode.handle_token(parser, token)
