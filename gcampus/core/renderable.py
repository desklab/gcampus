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

from functools import cached_property
from pathlib import Path
from typing import Type, ClassVar, Optional

from django.http import HttpRequest
from django.template.backends.base import BaseEngine
from django.template.backends.django import DjangoTemplates
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
