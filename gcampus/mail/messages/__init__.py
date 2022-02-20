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

import typing as t
from abc import ABC
from os import path

from premailer import transform
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpRequest
from django.template.loader import render_to_string

from gcampus.core import get_base_url
from gcampus.documents.utils import mock_request
from gcampus.mail.templatetags.mail import include_static


class EmailTemplate(ABC):
    template_path: str
    subject: str
    preheader: str
    stylesheet: str = "gcampusmail/styles/mail.css"

    def __init__(self, request: t.Optional[HttpRequest] = None):
        """
        :param request: Optional request instance. A request is required
            for context processors to work. If no request is provided,
            a mock request will be created.
        """
        self.request = request if request is not None else mock_request()

    def get_html_template(self) -> str:
        return path.join(self.template_path, "html.html")

    def get_text_template(self) -> str:
        return path.join(self.template_path, "text.html")

    def get_subject(self) -> str:
        # Make sure the subject is cast to a string. This will evaluate
        # lazy functions such as 'gettext_lazy'.
        return str(self.subject)

    def get_preheader(self) -> str:
        return str(self.preheader)

    def get_context(self, **kwargs) -> dict:
        context: dict = kwargs.copy()
        if "preheader" not in context:
            context["preheader"] = self.get_preheader()
        return context

    def get_stylesheet(self) -> str:
        return include_static(self.stylesheet)

    def render(self, using=None) -> t.Tuple[str, str]:
        """Render email templates

        :param using: Template engine passed to
            :func:`django.template.loader.render_to_string`.
        """
        context = self.get_context()
        html = render_to_string(
            self.get_html_template(), context=context, request=self.request, using=using
        )
        text = render_to_string(
            self.get_text_template(), context=context, request=self.request, using=using
        )
        # Some email clients still do not support styles defined in the
        # HTML '<head>' tag. Styles must be applied inline, i.e. using
        # the 'style="..."' attribute of the corresponding HTML
        # elements.
        inlined_html = transform(
            html, base_url=get_base_url(), css_text=self.get_stylesheet()
        )
        return text, inlined_html

    def as_message(self, to: t.List[str], using=None, **email_kwargs) -> EmailMessage:
        """Return Email Template as Email Message

        Returns a :class:`django.core.mail.EmailMessage` with both a
        plain text and a html alternative part.

        :param to: List of recipients
        :param using: Template engine passed to
            :func:`django.template.loader.render_to_string`.
        :param email_kwargs: Additional keyword arguments passed to
            ``EmailMessage``.
        """
        text, html = self.render(using=using)
        message = EmailMultiAlternatives(
            subject=self.get_subject(),
            body=text,
            to=to,
            **email_kwargs,
        )
        message.attach_alternative(html, "text/html")
        return message
