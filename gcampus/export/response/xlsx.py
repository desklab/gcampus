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

__all__ = ["XlsxResponse"]

import os
from numbers import Number
from typing import Tuple, IO, List, Optional

from django.urls import reverse
from django.utils.text import capfirst
from django.utils.timezone import localtime, make_naive
from django.utils.translation import gettext
from xlsxwriter import Workbook
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

from gcampus.core import get_base_url
from gcampus.core.models import (
    Parameter,
    ParameterType,
    Measurement,
    Water,
    TrophicIndex,
    BACHIndex,
    SaprobicIndex,
    StructureIndex,
)
from gcampus.core.models.index.base import WaterQualityIndex
from gcampus.core.models.parameter import ParameterTypeCategory
from gcampus.export.response.base import MeasurementExportResponse
from gcampus.export.workbook import ExportWorkbook
from gcampus.export.worksheet import ExportWorksheet, CellData, CellType


class XlsxResponse(MeasurementExportResponse):
    file_ending: str = "xlsx"

    @staticmethod
    def _get_measurement_url(measurement: Measurement) -> str:
        """Return the absolute (including base url) url to the detail
        view of the provided measurement.

        :param measurement: Instance of
            :class:`gcampus.core.models.Measurement`. The primary key
            (``pk``) has to be present.
        :returns: Absolut url as string
        """
        return get_base_url() + reverse(
            "gcampuscore:measurement-detail", kwargs={"pk": measurement.pk}
        )

    def _get_file(self, fd: int, filename: str) -> IO:
        """Create the XLSX file and return a file-like object containing
        the file.

        :param fd: File descriptor of the original file. Not used
            as :class:`xlsxwriter.Workbook` does not implement file
            descriptors.
        :param filename: Filename of the temporary XLSX file.
        :returns: File-like object (using :func:`open`)
        """
        os.close(fd)  # The file is handled by the Workbook class
        parameter_types: List[Tuple[int, str, str]] = (
            ParameterType.objects.order_by("pk")
            .only("pk", "name", "unit", "category")
            .values_list("pk", "name", "unit", "category")
        )
        workbook_options = {"constant_memory": True, "tmpdir": self._tempdir.name}
        with ExportWorkbook(filename, options=workbook_options) as wb:
            sheet: ExportWorksheet = wb.add_worksheet(gettext("Measurements"))
            self._write_header(sheet, parameter_types)
            row: Measurement
            for i, row in enumerate(self._rows):
                sheet.write_row_data(i + 1, self._get_row_data(row, parameter_types))
            wb.set_properties(
                {
                    "title": gettext("Measurement data from GewässerCampus"),
                    "author": gettext(
                        "GewässerCampus contributors, OpenStreetMap contributors"
                    ),
                    "company": "desklab gUG (haftungsbeschränkt)",
                    "created": make_naive(localtime()),
                    "comments": gettext("Export created with GewässerCampus"),
                    "hyperlink_base": get_base_url(),
                }
            )
        return open(filename, "rb")

    @staticmethod
    def _get_row_data(
        measurement: Measurement,
        parameter_types: List[Tuple[int, str, str]],
    ) -> List[CellData]:
        url = XlsxResponse._get_measurement_url(measurement)
        url_kwargs = {
            "string": f"#{measurement.pk:05d}",
            "tip": capfirst(gettext("open on GewässerCampus")),
        }
        row_data: List[CellData] = [
            CellData(url, CellType.url, kwargs=url_kwargs),
            CellData(measurement.name, CellType.string),
            CellData(measurement.time, CellType.datetime),
            CellData(measurement.location_name, CellType.string),
            CellData(measurement.water.display_name, CellType.string),
            CellData(measurement.water.get_flow_type_display(), CellType.string),
            CellData(measurement.water.get_water_type_display(), CellType.string),
            CellData(measurement.data_quality_warning, CellType.boolean),
        ]
        parameters: List[Parameter] = measurement.parameters.all()
        for pk, _, _, category in parameter_types:
            params: List[Parameter] = [
                param for param in parameters if param.parameter_type_id == pk
            ]
            value: Optional[Number] = None
            comment: Optional[str] = None
            count: int = len(params)
            cell_type: CellType = CellType.number
            if count > 0:
                comments: List[str] = []
                # Compute the mean of the parameter
                value = sum(map(lambda p: p.value, params)) / count
                if count > 1:
                    # Add comment for number of measurements used for
                    # averaging
                    comments.append(
                        gettext("Average of {count:d} measurements").format(count=count)
                    )
                # Add comments of each parameter
                comments += [p.comment for p in params if p.comment]
                if comments:
                    # Add comments seperated by a new line
                    comment = "\n".join(comments)
            if category == ParameterTypeCategory.BIOLOGICAL and count == 1:
                # Change value and corresponding cell type to an
                # integer as all biological parameters are counts and
                # the value is not an average.
                value = int(value)
                cell_type = CellType.integer
            row_data.append(CellData(value, cell_type, comment=comment))
        index: WaterQualityIndex
        for index in measurement.indices:
            value = classification = description = validity = None
            if index.valid_flow_type:
                validity = index.validity
                if index.validity > 0:
                    value = index.value
                    classification = index.classification
                    description = index.description
            row_data.append(CellData(value, CellType.number))
            row_data.append(CellData(classification, CellType.string))
            row_data.append(CellData(description, CellType.string))
            row_data.append(CellData(validity, CellType.percentage))
        row_data.append(CellData(measurement.comment, CellType.string))
        return row_data

    @staticmethod
    def _write_header(
        sheet: ExportWorksheet,
        parameter_types: List[Tuple[int, str, str]],
    ) -> int:
        """
        :returns: Total number of columns
        """
        cells = [
            Measurement._meta.verbose_name,
            (Measurement.name.field.verbose_name, 20),
            (Measurement.time.field.verbose_name, 20),
            (Measurement.location_name.field.verbose_name, 20),
            (gettext("Water name"), 20),
            (Water.flow_type.field.verbose_name, 20),
            (Water.water_type.field.verbose_name, 20),
            capfirst(gettext("data quality warning")),
        ]
        for _, name, unit, _ in parameter_types:
            if unit:
                name = f"{name!s} [{unit!s}]"
            cells.append(name)
        classification_str = str(WaterQualityIndex.classification.field.verbose_name)
        description_str = str(WaterQualityIndex.description.field.verbose_name)
        validity_str = str(WaterQualityIndex.validity.field.verbose_name)
        for index in (BACHIndex, SaprobicIndex, StructureIndex, TrophicIndex):
            name = str(index._meta.verbose_name)
            cells.append(name)
            cells.append(f"{name} ({classification_str})")
            cells.append(f"{name} ({description_str})")
            cells.append(f"{name} ({validity_str})")
        cells.append(Measurement.comment.field.verbose_name)
        sheet.write_header(0, cells)
