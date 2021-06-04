from django.contrib.gis import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from leaflet.admin import LeafletGeoAdmin

from gcampus.core.models import (
    Measurement,
    DataType,
    DataPoint,
    StudentToken,
    TeacherToken,
)
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def deactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    queryset.update(deactivated=True)


def reactivate_token(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    queryset.update(deactivated=False)


def hide(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    queryset.update(hidden=True)


def show(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    queryset.update(hidden=False)


deactivate_token.short_description = _("Deactivate selected tokens")
reactivate_token.short_description = _("Reactivate selected tokens")
hide.short_description = _("Hide selected items for all users")
show.short_description = _("Show selected items for all users")


class MeasurementAdmin(LeafletGeoAdmin):
    list_filter = ("hidden",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("location_name",)
    actions = [hide, show]


class DataTypeAdmin(admin.ModelAdmin):
    pass


class DataPointAdmin(admin.ModelAdmin):
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    list_filter = ("hidden",)
    default_manager_name = "all_objects"
    actions = [hide, show]


class StudentTokenAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


class TeacherTokenAdmin(admin.ModelAdmin):
    list_filter = ("deactivated",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    actions = [deactivate_token, reactivate_token]


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(StudentToken, StudentTokenAdmin)
admin.site.register(TeacherToken, TeacherTokenAdmin)
