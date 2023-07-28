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
from urllib.parse import urljoin

from django.utils.translation import gettext_lazy

from gcampus.core import get_base_url
from gcampus.mail.messages import EmailTemplate


class ConfirmationEmailTemplate(EmailTemplate):
    template_path: str = "gcampusmail/email_confirmation/base.html"
    subject: str = gettext_lazy("Email confirmation")
    preheader: str = gettext_lazy(
        "Please confirm your email address for GewässerCampus by clicking the link in "
        "this email."
    )

    def __init__(self, url: str, **kwargs):
        base_url: str = get_base_url()
        self.url = urljoin(base_url, url)
        super(ConfirmationEmailTemplate, self).__init__(**kwargs)

    def get_context(self, **kwargs) -> dict:
        if "url" not in kwargs:
            kwargs["url"] = self.url
        return super(ConfirmationEmailTemplate, self).get_context(**kwargs)
