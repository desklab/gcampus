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

from django.contrib.gis import admin

from gcampus.tools.models import MeasurementKit, Calibration


class MeasurementKitAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "identifier",
        "short_name",
    )


class CalibrationAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "measurement_kit",
        "parameter_type",
    )


admin.site.register(MeasurementKit, MeasurementKitAdmin)
admin.site.register(Calibration, CalibrationAdmin)
