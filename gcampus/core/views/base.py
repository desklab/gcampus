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

from typing import Optional

from django.views.generic.base import ContextMixin


class TitleMixin(ContextMixin):
    title: Optional[str] = None

    def get_title(self) -> str:
        return self.title

    def get_context_data(self, **kwargs):
        """Insert the page title into the context dict."""
        if 'page_title' not in kwargs:
            kwargs['page_title'] = self.get_title()
        return super().get_context_data(**kwargs)
