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

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from gcampus.auth.signals import token_user_logged_in


class GCampusAuthAppConfig(AppConfig):
    name = "gcampus.auth"
    label = "gcampusauth"
    verbose_name = _("GCampus Auth")

    def ready(self):
        from . import receivers  # imported to connect all receivers
        from .models import update_last_token_login

        token_user_logged_in.connect(update_last_token_login)
