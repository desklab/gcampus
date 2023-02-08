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

__all__ = ["CellType", "CellData", "ExportWorksheet"]

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Tuple, Callable, Any

from django.utils.timezone import is_naive, make_naive
from django.utils.translation import gettext as _
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet, cell_string_tuple

from gcampus.core.models.util import EMPTY

OptionalFormat = Optional[Format]


class CellType(Enum):
    integer = "integer"
    number = "number"
    datetime = "datetime"
    percentage = "percentage"
    string = "string"
    url = "url"
    boolean = "boolean"


@dataclass
class CellData:
    data: Any
    cell_type: CellType
    comment: Optional[str] = None
    kwargs: Optional[dict] = None

    @property
    def clean_data(self) -> Union[None, str, datetime, float, bool]:
        if self.data is None:
            return None
        if self.cell_type is CellType.string or self.cell_type is CellType.url:
            return str(self.data)
        elif self.cell_type is CellType.integer:
            return int(self.data)
        elif self.cell_type is CellType.number or self.cell_type is CellType.percentage:
            return float(self.data)
        elif self.cell_type is CellType.datetime:
            if not is_naive(self.data):
                return make_naive(self.data)
            return self.data
        elif self.cell_type is CellType.boolean:
            return bool(self.data)
        else:
            raise NotImplementedError(f"unknown cell type {self.cell_type}")


class ExportWorksheet(Worksheet):
    _header_format: OptionalFormat
    _integer_format: OptionalFormat
    _number_format: OptionalFormat
    _datetime_format: OptionalFormat
    _percentage_format: OptionalFormat

    def set_formats(
        self,
        header_format: OptionalFormat,
        integer_format: OptionalFormat,
        number_format: OptionalFormat,
        datetime_format: OptionalFormat,
        percentage_format: OptionalFormat,
    ):
        self._header_format = header_format
        self._integer_format = integer_format
        self._number_format = number_format
        self._datetime_format = datetime_format
        self._percentage_format = percentage_format

    @property
    def header_format(self) -> OptionalFormat:
        if not hasattr(self, "_header_format"):
            raise RuntimeError("must call set_formats before calling write_row_data")
        return self._header_format

    @property
    def integer_format(self) -> OptionalFormat:
        if not hasattr(self, "_integer_format"):
            raise RuntimeError("must call set_formats before calling write_row_data")
        return self._integer_format

    @property
    def number_format(self) -> OptionalFormat:
        if not hasattr(self, "_number_format"):
            raise RuntimeError("must call set_formats before calling write_row_data")
        return self._number_format

    @property
    def datetime_format(self) -> OptionalFormat:
        if not hasattr(self, "_datetime_format"):
            raise RuntimeError("must call set_formats before calling write_row_data")
        return self._datetime_format

    @property
    def percentage_format(self) -> OptionalFormat:
        if not hasattr(self, "_percentage_format"):
            raise RuntimeError("must call set_formats before calling write_row_data")
        return self._percentage_format

    @property
    def string_format(self) -> OptionalFormat:
        return None

    @property
    def url_format(self) -> OptionalFormat:
        return None

    @property
    def boolean_format(self) -> OptionalFormat:
        return None

    def write_header(self, row, header: List[Union[str, Tuple[str, float]]]):
        for col, cell in enumerate(header):
            if isinstance(cell, tuple):
                cell_text, min_width = cell
            else:
                cell_text = cell
                min_width = 10
            cell_text = str(cell_text)
            col_width = max(len(cell_text) + 2, min_width)
            error = self.write_string(
                row, col, cell_text, cell_format=self.header_format
            )
            if error:
                return error
            error = self.set_column(col, col, col_width)
            if error:
                return error

    def _get_method_format(
        self, cell_data: CellData
    ) -> Tuple[Callable, OptionalFormat]:
        cell_type = cell_data.cell_type
        fmt: OptionalFormat = getattr(self, f"{cell_type.value}_format", None)
        if cell_data.data is None:
            return self.write_blank, fmt
        if cell_type is CellType.integer:
            cell_type = CellType.number
        if cell_type is CellType.percentage:
            return self.write_number, fmt
        else:
            return getattr(self, f"write_{cell_type.value}"), fmt

    def write_row_data(self, row, row_data: List[CellData]):
        for col, cell_data in enumerate(row_data):
            method, cell_format = self._get_method_format(cell_data)
            kwargs = cell_data.kwargs or {}
            error = method(
                row, col, cell_data.clean_data, cell_format=cell_format, **kwargs
            )
            if error:
                return error
            if cell_data.comment not in EMPTY:
                error = self.write_comment(row, col, str(cell_data.comment))
                if error:
                    return error

    # Undecorated version of write_boolean().
    def _write_boolean(self, row, col, boolean, cell_format=None):

        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # Write previous row if in in-line string constant_memory mode.
        if self.constant_memory and row > self.previous_row:
            self._write_single_row(row)

        if boolean:
            value = _("yes")
        else:
            value = _("no")

        # Store the cell data in the worksheet data table.
        self.table[row][col] = cell_string_tuple(value, cell_format)

        return 0
