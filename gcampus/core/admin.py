from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from gcampus.core.models import Measurement, DataType, DataPoint, StudentToken, TeacherToken
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


class MeasurementAdmin(LeafletGeoAdmin):
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("location_name",)


class DataTypeAdmin(admin.ModelAdmin):
    pass


class DataPointAdmin(admin.ModelAdmin):
    readonly_fields = ADMIN_READ_ONLY_FIELDS

class StudentTokenAdmin(admin.ModelAdmin):
    pass

class TeacherTokenAdmin(admin.ModelAdmin):
    pass


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(StudentToken, StudentTokenAdmin)
admin.site.register(TeacherToken, TeacherTokenAdmin)
