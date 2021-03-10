from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from gcampus.core.models import Measurement, DataType, DataPoint
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


class MeasurementAdmin(LeafletGeoAdmin):
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("location_name",)

class DataTypeAdmin(admin.ModelAdmin):
    pass


class DataPointAdmin(admin.ModelAdmin):
    readonly_fields = ADMIN_READ_ONLY_FIELDS


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(DataPoint, DataPointAdmin)
