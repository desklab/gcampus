#  Copyright (C) 2022 desklab gUG (haftungsbeschränkt)
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
import dataclasses
from functools import cached_property
from pathlib import Path
from typing import Type, Optional, ClassVar, Tuple, Union, Dict, List

from django.http import HttpRequest
from django.template.backends.base import BaseEngine
from django.template.backends.django import DjangoTemplates
from django.utils.safestring import mark_safe


class Renderable:
    backend: Type[BaseEngine] = DjangoTemplates
    template_name: ClassVar[str]

    def get_context(self, **kwargs) -> dict:
        raise NotImplementedError("subclasses must implement get_context()")

    def get_template(self, template_name: str):
        return self.engine.get_template(template_name)

    @cached_property
    def engine(self) -> BaseEngine:
        return self.backend(
            {
                "APP_DIRS": True,
                "DIRS": [Path(__file__).parent / self.backend.app_dirname],  # noqa
                "NAME": "gcampustabs",
                "OPTIONS": {},
            }
        )

    def render(
        self,
        template_name: Optional[str] = None,
        context: Optional[dict] = None,
        request: Optional[HttpRequest] = None,
    ) -> str:
        template = self.get_template(template_name or self.template_name)
        context = context or self.get_context()
        return mark_safe(template.render(context, request=request).strip())

    __str__ = render
    __html__ = render


@dataclasses.dataclass
class Tab(Renderable):
    name: str
    url: Optional[str] = None
    disabled: bool = False
    active: bool = False

    # Class variables
    template_name: ClassVar[str] = "gcampuscore/components/tab.html"

    def get_context(self, **kwargs) -> dict:
        context: dict = dataclasses.asdict(self)
        context["class_list"]: List[str] = []
        context["attrs"]: List[str] = []
        if self.disabled:
            context["class_list"].append("disabled")
            context["attrs"].append('aria-disabled="true"')
        if self.active:
            context["class_list"].append("active")
            context["attrs"].append('aria-current="page"')
        if self.url:
            context["attrs"].append(f'href="{self.url!s}"')
        # Mark all attributes as safe to avoid double quotes
        context["attrs"] = map(mark_safe, context["attrs"])
        context.update(kwargs)
        return context


class TabNavigation(Renderable):
    template_name: ClassVar[str] = "gcampuscore/components/tab_navigation.html"
    tabs: Union[Tuple[Tab, ...], Dict[str, Tab]]

    def __init__(self, *tabs: Tab, **kwargs: Tab):
        """Tab navigation layout.

        The signature of this class allows passing multiple tabs
        (instances of :class:`gcampus.core.tabs.Tab`) as positional
        arguments or as keyword arguments resulting in named tabs that
        can easily be referred to by their name as a key.

        :param tabs: Tuple of :class:`gcampus.core.tabs.Tab` instances.
        :param kwargs: Multiple tabs passed as named keyword arguments.
        """
        if tabs and kwargs:
            raise ValueError(
                "Either positional or keyword arguments are accepted, but not both."
            )
        self.tabs = tabs if tabs else kwargs

    def __getitem__(self, item) -> Tab:
        return self.tabs[item]

    def __deepcopy__(self, memo):
        if isinstance(self.tabs, tuple):
            return TabNavigation(*copy.deepcopy(self.tabs, memo))
        elif isinstance(self.tabs, dict):
            return TabNavigation(**copy.deepcopy(self.tabs, memo))
        else:
            raise RuntimeError(f"Unsupported type of 'tabs': {type(self.tabs)}.")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__!s} tabs=({','.join(self.tabs)!s})>"

    def get_context(self, **kwargs) -> dict:
        context: dict = {
            "tabs": self.tabs.values() if isinstance(self.tabs, dict) else self.tabs
        }
        context.update(kwargs)
        return context
