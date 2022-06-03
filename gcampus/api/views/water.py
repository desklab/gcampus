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

__all__ = [
    "WaterLookupAPIViewSet",
    "OverpassLookupAPIViewSet",
    "WaterAPIViewSet",
]

from typing import List, Optional, Tuple

from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from gcampus.api import overpass
from gcampus.api.filtersets import WaterLookupFilterSet
from gcampus.api.overpass import Element
from gcampus.api.serializers import WaterSerializer, WaterListSerializer
from gcampus.api.utils import GeoLookupValue
from gcampus.api.views.mixins import MethodSerializerMixin
from gcampus.core.models import Water


class WaterLookupAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = Water.objects.order_by("name")
    serializer_class = WaterSerializer
    pagination_class = None
    filterset_class = WaterLookupFilterSet

    def list(self, request, *args, **kwargs):
        return super(WaterLookupAPIViewSet, self).list(request, *args, **kwargs)


class OverpassLookupAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    # Only return the OSM IDs
    queryset = Water.objects.only("osm_id")
    serializer_class = WaterSerializer
    pagination_class = None
    filterset_class = WaterLookupFilterSet

    def list(self, request: Request, **kwargs):
        """List all missing waters retrieved from the Overpass
        (OpenStreetMaps) API.

        :param request: Current request, provided automatically.
        :returns: Serialized GeoJSON representation of all missing
            waters in the bounding box provided as URL parameters.
        """
        # Construct a filter set and retrieve the GeoLookupValue
        # object from the current request.
        geo_lookup_value: GeoLookupValue = self._get_geo_lookup_value(request)
        # Construct the Overpass query using the GeoLookupValue
        # bounding box.
        overpass_query: str = self.get_overpass_query(
            geo_lookup_value.get_bbox_coordinates()
        )
        # Query the Overpass API
        result: List[Element] = overpass.query(overpass_query)
        waters: List[Water] = []
        with transaction.atomic():
            for element in result:
                try:
                    water = Water.objects.get(osm_id=element.osm_id)
                    water.update_from_element(element)
                    water.save()
                    waters.append(water)
                except Water.DoesNotExist:
                    water: Water = Water.from_element(element)
                    water.save()
                    waters.append(water)
        serializer = self.get_serializer(waters, many=True)
        return Response(serializer.data)

    def _get_geo_lookup_value(self, request) -> Optional[GeoLookupValue]:
        """Returns an instance of
        :class:`gcampus.api.utils.GeoLookupValue` for the current
        request.

        The method hijacks the filter backend's ``get_filterset``
        method to parse the request data.

        :returns: Instance of :class:`gcampus.api.utils.GeoLookupValue`.
        :rtype: gcampus.api.utils.GeoLookupValue
        :raises RuntimeError: If the filter set is invalid.
        """
        # Hijack the `DjangoFilterBackend.get_filterset` method to
        # retrieve an initialized instance of the relevant filter set.
        filterset: WaterLookupFilterSet = DjangoFilterBackend().get_filterset(
            request, self.get_queryset(), self
        )
        if not filterset.is_valid():
            # This code should never be reached. As the filter set is
            # already used in `self.filter_queryset` to retrieve the
            # database OSM IDs in `self.list`, code like this should
            # already have cause an exception.
            raise RuntimeError("Filter set is invalid.")
        return filterset.form.cleaned_data.get("geo")

    @staticmethod
    def get_overpass_query(bbox: Tuple[float, float, float, float]) -> str:
        """Construct an Overpass query using its query language.

        :param bbox: Tuple of coordinates used for bounding box corners.
        :type bbox: tuple[float, float, float, float]
        :returns: String query for Overpass.
        :rtype: str
        """
        a_lng, a_lat, b_lng, b_lat = bbox
        bbox_str: str = ",".join(f"{f:.5f}" for f in [a_lat, a_lng, b_lat, b_lng])
        return f"""
        [bbox:{bbox_str}][out:json];
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
        relation(bw.ways:"main_stream","outer","inner")->.relofways;
        way(r.relofways)->.waysinrels;
        (
          .ways;
          -
          .waysinrels;
        )->.filteredways;
        (
          .filteredways;
          .rels;
          node["natural"="spring"];
        );
        out geom;
        """


class WaterAPIViewSet(MethodSerializerMixin, viewsets.ModelViewSet):
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
            qs.defer("geometry")
        return qs

    def destroy(self, request, *args, **kwargs):
        """Disallow destroy action by returning
        :meth:`.http_method_not_allowed`.
        """
        return self.http_method_not_allowed(request, *args, **kwargs)
