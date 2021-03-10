from django.contrib.gis import admin

from gcampus.core.models import Measurement, DataType, DataPoint
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


class MeasurementAdmin(admin.OSMGeoAdmin):
    default_lon = 1022432.1417261
    default_lat = 6443998.3973475
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("location_name",)
    map_template = "gcampuscore/admin/osm.html"


class DataTypeAdmin(admin.ModelAdmin):
    pass


class DataPointAdmin(admin.ModelAdmin):
    readonly_fields = ADMIN_READ_ONLY_FIELDS


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(DataPoint, DataPointAdmin)
