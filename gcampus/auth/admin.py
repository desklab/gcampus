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
from gcampus.auth.models.email import BlockedEmail
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


@admin.action(description=_("Remove cached documents"))
def remove_cached_overview_documents(
    modeladmin: admin.ModelAdmin, request, qs: QuerySet
):
    qs.update(overview_document=None)


class CourseAdmin(admin.ModelAdmin):
    list_filter = ("email_verified",)
    search_fields = ("name", "school_name", "teacher_name")
    list_display = (
        "__str__",
        "name",
        "school_name",
        "teacher_name",
        "email_verified",
    )
    list_display_links = ("__str__",)
    inlines = [CourseTokenInline, AccessKeyInline]
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [remove_cached_overview_documents]


class AccessKeyAdmin(admin.ModelAdmin):
    list_filter = ("deactivated", "last_login")
    search_fields = ("course__name", "course__school_name", "course__teacher_name")
    list_display = (
        "masked_token",
        "course",
        "last_login",
        "deactivated",
    )
    list_display_links = ("masked_token",)
    filter_horizontal = ("permissions",)
    inlines = [MeasurementInline]
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


class CourseTokenAdmin(admin.ModelAdmin):
    list_filter = ("deactivated", "last_login")
    search_fields = ("course__name", "course__school_name", "course__teacher_name")
    list_display = (
        "masked_token",
        "course",
        "last_login",
        "deactivated",
    )
    list_display_links = ("masked_token",)
    filter_horizontal = ("permissions",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


class BlockedEmailAdmin(admin.ModelAdmin):
    list_filter = ("created_at", "updated_at")
    search_fields = ("email", "internal_comment")
    list_display = ("email", "internal_comment")
    readonly_fields = ADMIN_READ_ONLY_FIELDS


admin.site.register(Course, CourseAdmin)
admin.site.register(AccessKey, AccessKeyAdmin)
admin.site.register(CourseToken, CourseTokenAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(BlockedEmail, BlockedEmailAdmin)
