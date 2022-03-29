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

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy


class LinkedInlineMixin:
    readonly_fields = ("admin_link",)

    @admin.display(description=gettext_lazy("Admin link"))
    def admin_link(self, instance):
        info = self.model._meta.app_label, self.model._meta.model_name
        url = reverse("admin:%s_%s_change" % info, kwargs=dict(object_id=instance.pk))
        return format_html('<a href="{url}">{title!s}</a>', url=url, title=instance)
