from django.contrib.gis import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from leaflet.admin import LeafletGeoAdmin

from gcampus.core.models import (
    Measurement,
    DataType,
    DataPoint,
)
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def hide(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(hidden=True)


def show(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(hidden=False)


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


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(DataPoint, DataPointAdmin)
