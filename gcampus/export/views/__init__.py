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

from abc import ABC
from typing import Type

from django.db.models import QuerySet
from django.views import View
from django.views.generic.list import MultipleObjectMixin

from gcampus.core.filters import MeasurementFilterSet
from gcampus.core.models import Measurement
from gcampus.export.response.base import MeasurementExportResponse
from gcampus.export.response.xlsx import XlsxResponse


class DataExportView(MultipleObjectMixin, View, ABC):
    http_method_names = ["get"]
    model = Measurement
    object_list: QuerySet
    response_class: Type[MeasurementExportResponse]

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_set = MeasurementFilterSet(
            self.request.GET, queryset=queryset, request=self.request
        )
        return filter_set.qs.all()

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.response_class(self.object_list)


class XlsxExportView(DataExportView):
    response_class = XlsxResponse
