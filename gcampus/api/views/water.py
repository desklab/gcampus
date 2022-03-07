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

from django.conf import settings
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework_gis.pagination import GeoJsonPagination

from gcampus.api.apps import GCampusAPIAppConfig
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

    @method_decorator(cache_page(
        getattr(settings, "OVERPASS_CACHE", 60 * 60 * 24 * 2),
        cache=f"{GCampusAPIAppConfig.label}:waterlookup"
    ))
    def list(self, request, *args, **kwargs):
        return super(WaterLookupAPIViewSet, self).list(request, *args, **kwargs)

class WaterAPIViewSet(MethodSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Water.objects.order_by("name")
    serializer_class = WaterSerializer
    serializer_class_list = WaterListSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        qs: QuerySet = super(WaterAPIViewSet, self).get_queryset()
        if self.action == "list":
            # Do not load the geometry field for lists. Note that the
            # serializer for lists does not include the geometry field
            # for better performance.
            qs.defer(("geometry",))
        return qs
