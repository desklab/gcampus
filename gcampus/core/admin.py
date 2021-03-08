from django.contrib import admin
from gcampus.core.models import Measurement, DataType, DataPoint


class MeasurementAdmin(admin.ModelAdmin):
    pass


class DataTypeAdmin(admin.ModelAdmin):
    pass


class DataPointAdmin(admin.ModelAdmin):
    pass


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(DataPoint, DataPointAdmin)
