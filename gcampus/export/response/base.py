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

import tempfile
from abc import ABC
from typing import Iterable, IO

from django.db.models import QuerySet
from django.http import FileResponse
from django.utils.translation import gettext


class MeasurementExportResponse(FileResponse, ABC):
    # Used for filename, must be implemented by subclasses
    file_ending: str

    def __init__(self, measurements: QuerySet, *args, **kwargs):
        if "filename" not in kwargs:
            # Add filename
            kwargs["filename"] = gettext("measurements.{file_ending!s}").format(
                file_ending=self.file_ending
            )
        super().__init__(*args, **kwargs)
        # Transform measurement query set into row iterator
        self._rows: Iterable = self._get_rows(measurements)
        # Create a temporary directory for all temporary files
        self._tempdir = tempfile.TemporaryDirectory()
        # File used for final export
        fd, filename = tempfile.mkstemp(
            dir=self._tempdir.name,  # will be deleted at the end
            suffix=f".{self.file_ending}",  # use file ending as suffix
        )
        # _get_file must return a file-like object
        self.streaming_content = self._get_file(fd, filename)
        # TemporaryDirectory.cleanup will try to remove the directory
        self._resource_closers.append(self._tempdir.cleanup)

    def _get_rows(self, measurements: QuerySet) -> Iterable:
        raise NotImplementedError("subclasses must implement _get_rows(measurements)")

    def _get_file(self, fd: int, filename: str) -> IO:
        # Use 'os.fdopen(handle, "wb")' to make use of the file descriptor
        raise NotImplementedError("subclasses must implement _get_file(fd)")
