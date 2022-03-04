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

__all__ = ["WaterLookupAPIViewSet", "WaterAPIViewSet"]

from rest_framework import viewsets, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework_gis.pagination import GeoJsonPagination

from gcampus.api.filtersets import WaterLookupFilterSet
from gcampus.api.serializers import WaterSerializer, WaterListSerializer
from gcampus.api.views.mixins import MethodSerializerMixin
from gcampus.core.models import Water


class _LimitedGeoJsonPagination(GeoJsonPagination):
    page_size = 2


class WaterLookupAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = Water.objects.order_by("name")
    serializer_class = WaterSerializer
    pagination_class = _LimitedGeoJsonPagination
    filterset_class = WaterLookupFilterSet


class WaterAPIViewSet(MethodSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Water.objects.order_by("name")
    serializer_class = WaterSerializer
    serializer_class_list = WaterListSerializer
    pagination_class = PageNumberPagination
