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
from typing import Tuple, IO, List

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
from gcampus.core.models.water import FlowType
from gcampus.export.response.base import MeasurementExportResponse


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
            .only("pk", "name", "unit")
            .values_list("pk", "name", "unit")
        )
        workbook_options = {"constant_memory": True, "tmpdir": self._tempdir.name}
        with Workbook(filename, options=workbook_options) as wb:
            sheet = wb.add_worksheet(gettext("Measurements"))
            bold_format = wb.add_format({"bold": True})
            number_format = wb.add_format()
            number_format.set_num_format(2)
            datetime_format = wb.add_format()
            datetime_format.set_num_format(22)
            percentage_format = wb.add_format()
            percentage_format.set_num_format(10)
            cols = self._write_header(sheet, parameter_types, bold_format)
            row: Measurement
            for i, row in enumerate(self._rows):
                self._write_row(
                    sheet,
                    i + 1,
                    row,
                    parameter_types,
                    number_format,
                    datetime_format,
                    percentage_format,
                )
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
    def _write_row(
        sheet: Worksheet,
        row_number: int,
        measurement: Measurement,
        parameter_types: List[Tuple[int, str, str]],
        number_format: Format,
        datetime_format: Format,
        percentage_format: Format,
    ):
        sheet.write_url(
            row_number,
            0,
            XlsxResponse._get_measurement_url(measurement),
            string=f"#{measurement.pk:05d}",
            tip=capfirst(gettext("open on GewässerCampus")),
        )
        sheet.write_string(row_number, 1, measurement.name)
        sheet.write_datetime(
            row_number, 2, make_naive(measurement.time), cell_format=datetime_format
        )
        sheet.write_string(row_number, 3, str(measurement.location_name))
        sheet.write_string(row_number, 4, str(measurement.water.display_name))
        sheet.write_string(
            row_number, 5, capfirst(measurement.water.get_flow_type_display())
        )
        sheet.write_boolean(row_number, 6, measurement.data_quality_warning)
        parameters: List[Parameter] = measurement.parameters.all()
        offset = 7
        # Write the numeric value of all parameters
        for pk, _, _ in parameter_types:
            params: List[Parameter] = [
                param for param in parameters if param.parameter_type_id == pk
            ]
            if params:
                comments: List[str] = []
                count = len(params)
                # Compute the mean of the parameter
                mean = sum(map(lambda p: p.value, params)) / count
                if count > 1:
                    # Add comment for number of measurements used for
                    # averaging
                    comments.append(
                        gettext("Average of {count:d} measurements").format(count=count)
                    )
                # Add comments of each parameter
                comments += [p.comment for p in params if p.comment]
                sheet.write_number(row_number, offset, mean, cell_format=number_format)
                if comments:
                    # Add comments seperated by a new line
                    sheet.write_comment(row_number, offset, "\n".join(comments))
            else:
                sheet.write_blank(row_number, offset, None, cell_format=number_format)
            offset += 1
        index: WaterQualityIndex
        for index in measurement.indices:
            if not index.valid_flow_type:
                # Index is not valid for this flow type. Write blank
                # values and continue
                sheet.write_blank(row_number, offset, None, cell_format=number_format)
                offset += 1
                sheet.write_blank(
                    row_number, offset, None, cell_format=percentage_format
                )
                offset += 1
                continue
            if index.validity > 0:
                sheet.write_number(
                    row_number, offset, index.value, cell_format=number_format
                )
            else:
                # Write blank value, validity is too low
                sheet.write_blank(row_number, offset, None, cell_format=number_format)
            offset += 1
            sheet.write_number(
                row_number, offset, index.validity, cell_format=percentage_format
            )
            offset += 1
        sheet.write_string(row_number, offset, measurement.comment)

    @staticmethod
    def _write_header(
        sheet: Worksheet,
        parameter_types: List[Tuple[int, str, str]],
        format: Format,
    ) -> int:
        """
        :returns: Total number of columns
        """
        cells = [
            gettext("ID"),
            Measurement.name.field.verbose_name,
            Measurement.time.field.verbose_name,
            Measurement.location_name.field.verbose_name,
            gettext("Water name"),
            Water.flow_type.field.verbose_name,
            capfirst(gettext("data quality warning")),
        ]
        for _, name, unit in parameter_types:
            if unit:
                name = f"{name!s} [{unit!s}]"
            cells.append(name)
        validity_str = str(WaterQualityIndex.validity.field.verbose_name)
        for index in (BACHIndex, SaprobicIndex, StructureIndex, TrophicIndex):
            name = str(index._meta.verbose_name)
            cells.append(name)
            cells.append(f"{name} ({validity_str})")
        cells.append(Measurement.comment.field.verbose_name)
        for i, cell in enumerate(cells):
            # call 'str(cell)' to evaluate lazy translations
            text = str(cell)
            col_width = max(len(text) + 2, 10)
            if 1 <= i <= 5:
                # Increase cell width for names and time
                col_width = max(col_width, 20)
            sheet.write_string(0, i, text, cell_format=format)
            sheet.set_column(i, i, col_width)
        return len(cells)
