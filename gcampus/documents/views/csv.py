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

__all__ = ["CSVListView"]

import csv
from io import StringIO
from typing import Tuple, Optional, Iterator

from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.list import MultipleObjectMixin

from gcampus.core.filters import MeasurementFilterSet
from gcampus.core.models import Water
from gcampus.core.models.measurement import Measurement, ParameterType


class CSVListView(MultipleObjectMixin, View):
    model = Measurement
    queryset = Measurement.objects.all()
    ordering: Tuple[str, ...] = ("pk",)
    parameter_types: Tuple[str, ...]
    values: QuerySet
    response_class = StreamingHttpResponse
    content_type: str = "text/csv"

    def get(self, request):
        self.parameter_types: Tuple[str, ...] = tuple(
            ParameterType.objects.values_list("name", flat=True).order_by("pk")
        )
        self.values = self.get_queryset()
        return self.render_to_response(_("measurements.csv"))

    def render_to_response(self, filename, **response_kwargs):
        response_kwargs.setdefault("content_type", self.content_type)
        return self.response_class(
            streaming_content=self._stream(),
            headers={"Content-Disposition": f"attachment; filename={filename}"},
            **response_kwargs,
        )

    def _stream(self):
        with StringIO() as buffer:
            writer = csv.DictWriter(
                buffer,
                delimiter=",",
                quoting=csv.QUOTE_ALL,
                fieldnames=self.get_headers(),
            )
            writer.writeheader()
            for row in self.get_rows():
                writer.writerow(row)  # write the row to the buffer
                buffer.seek(0)  # reset buffer to beginning
                yield buffer.read()
                # Again, reset buffer to beginning and delete its
                # content.
                buffer.seek(0)
                buffer.truncate()

    def get_rows(self) -> Iterator[dict]:
        current: Optional[dict] = None
        for measurement in self.values:
            measurement = self._replace_nones_with_str(measurement)
            if current is not None and current["id"] != measurement["pk"]:
                yield current
                current = None
            if current is None:
                water_name = Water.get_water_name(
                    measurement["water__name"], measurement["water__water_type"]
                )
                current = {
                    "id": measurement["pk"],
                    "name": measurement["name"],
                    "location_name": measurement["location_name"],
                    "water_name": water_name,
                    "time": measurement["time"],
                }
                current.update({param_name: "" for param_name in self.parameter_types})
            parameter_value = measurement["parameters__value"]
            if parameter_value != "":
                parameter_name = measurement["parameters__parameter_type__name"]
                current[parameter_name] = parameter_value
        yield current

    def get_headers(self) -> Tuple[str, ...]:
        headers = ("id", "name", "location_name", "water_name", "time")
        return headers + self.parameter_types

    def get_queryset(self):
        filter_set = MeasurementFilterSet(
            self.request.GET, queryset=self.queryset, request=self.request
        )
        queryset: QuerySet = filter_set.qs.values(
            "pk",
            "name",
            "location_name",
            "water__name",
            "water__water_type",
            "time",
            "parameters__value",
            "parameters__parameter_type__name",
        )

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    @staticmethod
    def _replace_nones_with_str(some_dict: dict) -> dict:
        """Replaces ``None`` with empty strings"""
        return {
            key: ("" if value is None else value) for key, value in some_dict.items()
        }
