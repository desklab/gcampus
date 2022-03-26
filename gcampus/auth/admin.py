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

from django.contrib.gis import admin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _, gettext_lazy

from gcampus.admin.options import LinkedInlineMixin
from gcampus.auth.models import (
    AccessKey,
    CourseToken,
)
from gcampus.core.admin import MeasurementInline
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def deactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(deactivated=True)


def reactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(deactivated=False)


deactivate_token.short_description = _("Deactivate selected tokens")
reactivate_token.short_description = _("Reactivate selected tokens")


class AccessKeyInline(LinkedInlineMixin, admin.TabularInline):
    model = AccessKey
    extra = 0


class AccessKeyAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    inlines = [MeasurementInline]
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


class CourseTokenAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    inlines = [AccessKeyInline]
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


admin.site.register(AccessKey, AccessKeyAdmin)
admin.site.register(CourseToken, CourseTokenAdmin)
