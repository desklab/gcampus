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
import copy
from typing import Optional

from django.views.generic.base import ContextMixin

from gcampus.core.tabs import TabNavigation


class TitleMixin(ContextMixin):
    title: Optional[str] = None

    def get_title(self) -> str:
        return self.title

    def get_context_data(self, **kwargs):
        """Insert the page title into the context dict."""
        kwargs.setdefault("page_title", self.get_title())
        return super().get_context_data(**kwargs)


class TabsMixin(ContextMixin):
    #: Required: Instance of :class:`gcampus.core.tabs.TabNavigation`.
    tabs: TabNavigation
    #: If set, the :meth:`.get_tabs` method will automatically set the
    #: tab with the provided key as ``active``.
    current_tab_name: Optional[str] = None

    def get_tabs(self) -> TabNavigation:
        """Get tabs for current instance. The tabs are a deep copy of
        the class attribute :attr:`.tabs` to avoid mutation of other
        instances.

        To change a tab (e.g. set its url), first retrieve the deep
        copy (i.e. calling the super method) and then modify the tabs.
        """
        tabs: TabNavigation = copy.deepcopy(self.tabs)
        if self.current_tab_name:
            tabs[self.current_tab_name].active = True
        return tabs

    def get_context_data(self, **kwargs) -> dict:
        """Insert the tabs into the context dict."""
        kwargs.setdefault("tabs", self.get_tabs())
        return super(TabsMixin, self).get_context_data(**kwargs)
