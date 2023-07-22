#  Copyright (C) 2022 desklab gUG (haftungsbeschränkt)
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
import csv
import os
from typing import Iterable, IO, Tuple, Union

from django.db.models import QuerySet
from django.utils import translation
from django.utils.timezone import localtime

from gcampus.core.models import Parameter, Measurement, Water, ParameterType
from gcampus.core.models.index.base import WaterQualityIndex
from gcampus.export.response.base import MeasurementExportResponse


class CsvResponse(MeasurementExportResponse):
    file_ending = "csv"
    fieldnames: Tuple[str, ...] = (
        "type",
        "unit",
        "value",
        "time",
        "measurement_id",
        "water_id",
        "water_name",
        "flow_type",
        "water_type",
        "parameter_quality_warning",
        "index_validity",
        "note",
        "full_type_name",
        "measurement_note",
    )

    def __init__(self, *args, **kwargs):
        # Ensure reproducibility by fixing the language. Some
        # translations may be used in the output (namely, the verbose
        # name of the indices).
        with translation.override("en"):
            super().__init__(*args, **kwargs)

    def _get_rows(
        self, measurements: QuerySet
    ) -> Iterable[Union[Parameter, WaterQualityIndex]]:
        for measurement in super()._get_rows(measurements):
            for parameter in measurement.parameters.all():
                yield parameter
            index: WaterQualityIndex
            for index in measurement.indices:
                if index.validity > 0 and index.valid_flow_type:
                    # Skip all invalid indices
                    yield index

    def _get_file(self, fd: int, filename: str) -> IO:
        with os.fdopen(fd, "w+") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=self.fieldnames,
                delimiter=",",
                quoting=csv.QUOTE_ALL,
            )
            writer.writeheader()
            for row in self._rows:
                writer.writerow(self._get_row_dict(row))
        return open(filename, "rb")

    @staticmethod
    def _get_row_dict(row: Union[Parameter, WaterQualityIndex]) -> dict:
        measurement: Measurement = row.measurement
        water: Water = measurement.water
        data: dict = {
            "value": row.value,
            "time": localtime(row.measurement.time),
            "measurement_id": measurement.pk,
            "water_id": water.pk,
            "water_name": str(water.display_name),
            "flow_type": str(water.flow_type),
            "water_type": str(water.water_type),
            "parameter_quality_warning": measurement.parameter_quality_warning,
            "measurement_note": str(measurement.comment),
        }
        if isinstance(row, Parameter):
            parameter_type: ParameterType = row.parameter_type
            data.update(
                {
                    "type": str(parameter_type.identifier),
                    "unit": str(parameter_type.unit),
                    "note": str(row.comment),
                    "full_type_name": str(parameter_type.name),
                }
            )
        else:  # 'row' has to be of type 'WaterQualityIndex'
            data.update(
                {
                    "type": str(row._meta.verbose_name),
                    "index_validity": row.validity,
                    "full_type_name": str(row._meta.verbose_name),
                }
            )
        return data
