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

__all__ = [
    "WaterLookupAPIViewSet",
    "OverpassLookupAPIViewSet",
    "WaterAPIViewSet",
]

from typing import List, Optional, Tuple

from django.conf import settings
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import utils
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

from gcampus.api.filtersets import WaterLookupFilterSet
from gcampus.api.serializers import WaterSerializer, WaterListSerializer
from gcampus.api.utils import GeoLookupValue
from gcampus.api.views.mixins import MethodSerializerMixin
from gcampus.core.models import Water


class WaterLookupAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = Water.objects.order_by("name")
    serializer_class = WaterSerializer
    pagination_class = None
    filterset_class = WaterLookupFilterSet

    @method_decorator(cache_page(getattr(settings, "OVERPASS_CACHE", 60 * 60 * 24 * 2)))
    def list(self, request, *args, **kwargs):
        return super(WaterLookupAPIViewSet, self).list(request, *args, **kwargs)


class OverpassLookupAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    # Only return the OSM IDs
    queryset = Water.objects.order_by("name").only("osm_id")
    pagination_class = None
    filterset_class = WaterLookupFilterSet

    def list(self, request: Request, **kwargs):
        queryset: QuerySet = self.filter_queryset(self.get_queryset())
        osm_ids: List[int] = [water.osm_id for water in queryset.all()]
        geo_lookup_value: GeoLookupValue = self._get_geo_lookup_value(request)
        query: str = self.get_overpass_query(geo_lookup_value.get_bbox_coordinates())
        # TODO perform overpass query,
        #   create new db entries and return them

    def _get_geo_lookup_value(self, request) -> Optional[GeoLookupValue]:
        filterset: WaterLookupFilterSet = DjangoFilterBackend().get_filterset(
            request, self.get_queryset(), self
        )
        if not filterset.is_valid():
            raise utils.translate_validation(filterset.errors)
        return filterset.form.cleaned_data.get("geo")

    @staticmethod
    def get_overpass_query(bbox: Tuple[float, float, float, float]) -> str:
        bbox_str: str = ",".join(f"{f:.4f}" for f in bbox)
        return f"""
        [bbox:{bbox_str}]
        (
          way["natural"="water"]
            ["water"!="river"]
            ["water"!="stream"]
            ["water"!="canal"]
            ["water"!="ditch"]
            ["water"!="drain"];
          way["natural"="wetland"];
          way["natural"="coastline"];
          way["natural"="bay"];
          way["waterway"="river"];
          way["waterway"="stream"];
          way["waterway"="tidal_channel"];
          way["waterway"="canal"];
          way["waterway"="drain"];
          way["waterway"="ditch"];
        )->.ways;
        (
          relation["natural"="water"]
            ["water"!="river"]
            ["water"!="stream"]
            ["water"!="canal"]
            ["water"!="ditch"]
            ["water"!="drain"];
          relation["natural"="wetland"];
          relation["natural"="coastline"];
          relation["natural"="bay"];
          relation["waterway"="river"];
          relation["waterway"="stream"];
          relation["waterway"="tidal_channel"];
          relation["waterway"="canal"];
          relation["waterway"="drain"];
          relation["waterway"="ditch"];
        )->.rels;
        node(w.ways);
        way(r.rels)->.wrels;
        node(w.wrels);
        (
          .ways;
          .rels;
          node["natural"="spring"];
        );
        out geom;
        """


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
