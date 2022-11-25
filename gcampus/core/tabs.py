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
from django.urls import reverse
from django.utils.safestring import mark_safe


class Renderable:
    """Mixin for renderable classes. Subclasses must implement the
    method :meth:`.get_context` and set the attribute
    :attr:`.template_name` or alternatively overwrite the
    :meth:`.get_template` method.

    By calling ``str(instance)`` on an instance of a subclass, the
    HTML content is rendered. This can be used for example in templates
    with ``{{ instance }}``.
    """

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
    #: Name of the tab (displayed in HTML output)
    name: str
    #: Optional view name. May require additional arguments before
    #: calling :meth:`django.urls.reverse`. See
    #: :attr:`.vn_requires_args` for mor information.
    view_name: Optional[str] = None
    #: Optional url. If set, the :attr:`.view_name` attribute is
    #: ignored.
    url: Optional[str] = None
    #: Display the tab as disabled. By default, tabs are not disabled.
    disabled: bool = False
    #: Display the tab as active. By default, tabs are not active.
    active: bool = False
    #: If true, the :meth:`.get_context` method will not use the
    #: :attr:`.view_name` attribute even if no url is provided. This
    #: attribute indicates that additional arguments (e.g. the primary
    #: key of an object) is required for reversing the view name.
    #: To apply additional arguments,
    #: see :meth:`.set_url_from_view_name`.
    vn_requires_args: bool = False

    # Class variables
    template_name: ClassVar[str] = "gcampuscore/components/tab.html"

    def get_url_from_view_name(
        self,
        fmt: Optional[dict] = None,
        reverse_args: Optional[tuple] = None,
        reverse_kwargs: Optional[dict] = None,
    ) -> str:
        """Return the reverse for :attr:`.view_name` with additional
        arguments passed to :meth:`django.urls.reverse`.

        :param fmt: Optional dictionary used to format the view name
            string.
        :param reverse_args: Arguments passed as ``args`` to
            :meth:`django.urls.reverse`.
        :param reverse_kwargs: Keyword arguments passed as ``kwargs``
            to :meth:`django.urls.reverse`.
        """
        if self.view_name is None:
            raise ValueError("'view_name' is not set.")
        if fmt is not None:
            view_name = self.view_name.format(**fmt)
        else:
            view_name = self.view_name
        return reverse(view_name, args=reverse_args, kwargs=reverse_kwargs)

    def set_url_from_view_name(
        self,
        fmt: Optional[dict] = None,
        reverse_args: Optional[tuple] = None,
        reverse_kwargs: Optional[dict] = None,
    ):
        """Set :attr:`.url` using the reverse for :attr:`.view_name`
        with additional arguments passed to :meth:`django.urls.reverse`.

        Instead of :meth:`.get_url_from_view_name`, this method sets the
        :attr:`.url` attribute in-place and returns nothing.

        :param fmt: Optional dictionary used to format the view name
            string.
        :param reverse_args: Arguments passed as ``args`` to
            :meth:`django.urls.reverse`.
        :param reverse_kwargs: Keyword arguments passed as ``kwargs``
            to :meth:`django.urls.reverse`.
        """
        self.url = self.get_url_from_view_name(
            fmt=fmt, reverse_args=reverse_args, reverse_kwargs=reverse_kwargs
        )

    def get_context(self, **kwargs) -> dict:
        """Context for rendering the tab. Uses
        :meth:`dataclasses.asdict` to transform the attributes of this
        dataclass into a dictionary.
        """
        context: dict = dataclasses.asdict(self)
        context["class_list"]: List[str] = []
        context["attrs"]: List[str] = []
        url = self.url
        if self.view_name is not None and url is None and not self.vn_requires_args:
            url = self.get_url_from_view_name()
        if self.disabled:
            context["class_list"].append("disabled")
            context["attrs"].append('aria-disabled="true"')
        if self.active:
            context["class_list"].append("active")
            context["attrs"].append('aria-current="page"')
        if self.url:
            context["attrs"].append(f'href="{url!s}"')
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
        """Deep copies are required when using this class as a class
        attribute, for examples in view classes. This prevents mutating
        the tabs of other class instances.
        """
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
