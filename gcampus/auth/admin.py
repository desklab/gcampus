from django.contrib.gis import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from gcampus.auth.models import (
    StudentToken,
    TeacherToken,
)
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def deactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(deactivated=True)


def reactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(deactivated=False)


deactivate_token.short_description = _("Deactivate selected tokens")
reactivate_token.short_description = _("Reactivate selected tokens")


class StudentTokenAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


class TeacherTokenAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


admin.site.register(StudentToken, StudentTokenAdmin)
admin.site.register(TeacherToken, TeacherTokenAdmin)
