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

from django.contrib.auth.admin import UserAdmin
from django.contrib.gis import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from gcampus.auth.models import AccessKey, CourseToken, User, Course
from gcampus.core.admin import MeasurementInline
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def deactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(deactivated=True)


def reactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(deactivated=False)


deactivate_token.short_description = _("Deactivate selected tokens")
reactivate_token.short_description = _("Reactivate selected tokens")


class AccessKeyInline(admin.TabularInline):
    show_change_link = True
    model = AccessKey
    fields = ("token", "deactivated")
    extra = 0


class CourseTokenInline(admin.TabularInline):
    show_change_link = True
    model = CourseToken
    fields = ("token", "deactivated")
    extra = 0


class CourseInline(admin.TabularInline):
    show_change_link = True
    model = Course
    extra = 0


class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseTokenInline, AccessKeyInline]
    readonly_fields = ADMIN_READ_ONLY_FIELDS


class AccessKeyAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    filter_horizontal = ("permissions",)
    inlines = [MeasurementInline]
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


class CourseTokenAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    filter_horizontal = ("permissions",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


admin.site.register(Course, CourseAdmin)
admin.site.register(AccessKey, AccessKeyAdmin)
admin.site.register(CourseToken, CourseTokenAdmin)
admin.site.register(User, UserAdmin)
