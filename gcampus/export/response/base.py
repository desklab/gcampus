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

__all__ = ["MeasurementExportResponse"]

import tempfile
from abc import ABC
from typing import Iterable, IO, Tuple

from django.db.models import QuerySet, Prefetch
from django.http import FileResponse
from django.utils.translation import gettext

from gcampus.core.models import Parameter


class MeasurementExportResponse(FileResponse, ABC):
    # Used for filename, must be implemented by subclasses
    file_ending: str
    database_chunk_size: int = 2000
    values: Tuple[str, ...] = (
        "pk",
        "name",
        "location_name",
        "water_id",
        "water__name",
        "water__flow_type",
        "water__water_type",
        "time",
        "comment",
        "parameter_quality_warning",
    )

    def __init__(self, measurements: QuerySet, *args, as_attachment=True, **kwargs):
        if "filename" not in kwargs:
            # Add filename
            kwargs["filename"] = gettext("measurements.{file_ending!s}").format(
                file_ending=self.file_ending
            )
        super().__init__(*args, as_attachment=as_attachment, **kwargs)
        # Transform measurement query set into row iterator
        self._rows: Iterable = self._get_rows(measurements)
        # Create a temporary directory for all temporary files
        self._tempdir = tempfile.TemporaryDirectory()
        # File used for final export
        fd, filename = tempfile.mkstemp(
            dir=self._tempdir.name,  # will be deleted at the end
            suffix=f".{self.file_ending}",  # use file ending as suffix
        )
        try:
            # _get_file must return a file-like object
            self.streaming_content = self._get_file(fd, filename)
        finally:
            # If the line above fails, the temporary directory should
            # still be added to the resource closers.
            # TemporaryDirectory.cleanup will try to remove the directory
            self._resource_closers.append(self._tempdir.cleanup)

    def _get_rows(self, measurements: QuerySet) -> Iterable:
        parameter_queryset = Parameter.objects.select_related("parameter_type").only(
            "value",
            "parameter_type_id",
            "parameter_type__name",
            "parameter_type__unit",
            "parameter_type__identifier",
            # 'measurement_id' seems to be required to assign the
            # parameters to their measurements. If not provided here,
            # the field will be fetched later.
            "measurement_id",
            "comment",
        )
        return (
            measurements.select_related("water")
            .only(*self.values)
            .prefetch_related(
                # Prefetch parameters with 'parameter_queryset' to limit
                # number of database requests
                Prefetch("parameters", queryset=parameter_queryset),
                "bach_index",
                "saprobic_index",
                "structure_index",
                "trophic_index",
            )
            .iterator(chunk_size=self.database_chunk_size)
        )

    def _get_file(self, fd: int, filename: str) -> IO:
        raise NotImplementedError("subclasses must implement _get_file(fd)")
