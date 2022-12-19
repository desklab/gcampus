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

from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from gcampus.export.worksheet import ExportWorksheet


class ExportWorkbook(Workbook):
    worksheet_class = ExportWorksheet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_formats()

    def _init_formats(self):
        self.header_format = self.add_format({"bold": True})
        self.number_format = self.add_format()
        self.number_format.set_num_format(2)
        self.datetime_format = self.add_format()
        self.datetime_format.set_num_format(22)
        self.percentage_format = self.add_format()
        self.percentage_format.set_num_format(9)

    def _add_sheet(self, *args, **kwargs):
        worksheet: Worksheet = super()._add_sheet(*args, **kwargs)
        if isinstance(worksheet, ExportWorksheet):
            worksheet.set_formats(
                self.header_format,
                self.number_format,
                self.datetime_format,
                self.percentage_format,
            )
        return worksheet
