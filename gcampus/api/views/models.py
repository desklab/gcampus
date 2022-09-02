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

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from gcampus.api.filtersets import MeasurementAPIFilterSet
from gcampus.api.serializers import (
    MeasurementSerializer,
    ParameterTypeSerializer,
    ParameterSerializer,
    MeasurementListSerializer,
)
from gcampus.api.views.mixins import MethodSerializerMixin
from gcampus.core.models import Measurement, ParameterType, Parameter


class MeasurementAPIViewSet(MethodSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Measurement.objects.order_by("time")
        .select_related("water")
        .only("location", "water_id", "water__flow_type", "id")
    )
    serializer_class = MeasurementSerializer

    # Use a minimal serializer for lists. This serializer only includes
    # the bare minimum used for displaying the measurements on a map.
    serializer_class_list = MeasurementListSerializer
    # Pagination is disabled such that the api works better with
    # the map view.
    pagination_class = None
    # Measurement filter set used to filter for specific waters.
    filterset_class = MeasurementAPIFilterSet


class ParameterTypeAPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ParameterType.objects.order_by("name")
    serializer_class = ParameterTypeSerializer
    pagination_class = PageNumberPagination


class ParameterAPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parameter.objects.order_by("updated_at").select_related("parameter_type")
    serializer_class = ParameterSerializer
    pagination_class = PageNumberPagination
