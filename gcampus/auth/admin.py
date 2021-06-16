from django.contrib.gis import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from gcampus.auth.models import (
    AccessKey,
    CourseToken,
)
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def deactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(deactivated=True)


def reactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(deactivated=False)


deactivate_token.short_description = _("Deactivate selected tokens")
reactivate_token.short_description = _("Reactivate selected tokens")


class AccessKeyAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


class CourseTokenAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


admin.site.register(AccessKey, AccessKeyAdmin)
admin.site.register(CourseToken, CourseTokenAdmin)
