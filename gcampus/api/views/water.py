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
    queryset = Water.objects.only("osm_id")
    pagination_class = None
    filterset_class = WaterLookupFilterSet
    default_water_name: str = gettext_lazy("Unnamed water")
    unnamed_waters: Dict[str, str] = {
        "wetland": gettext_lazy("Unnamed wetland"),
        "coastline": gettext_lazy("Unnamed coastline"),
        "bay": gettext_lazy("Unnamed bay"),
        "river": gettext_lazy("Unnamed river"),
        "stream": gettext_lazy("Unnamed stream"),
        "tidal_channel": gettext_lazy("Unnamed tidal channel"),
        "canal": gettext_lazy("Unnamed canal"),
        "drain": gettext_lazy("Unnamed drain"),
        "ditch": gettext_lazy("Unnamed ditch"),
        "lagoon": gettext_lazy("Unnamed lagoon"),
        "oxbow": gettext_lazy("Unnamed oxbow"),
        "lake": gettext_lazy("Unnamed lake"),
        "basin": gettext_lazy("Unnamed basin"),
        "harbour": gettext_lazy("Unnamed harbour"),
        "pond": gettext_lazy("Unnamed pond"),
        "reservoir": gettext_lazy("Unnamed reservoir"),
        "wastewater": gettext_lazy("Unnamed wastewater"),
    }

    def list(self, request: Request, **kwargs):
        """List all missing waters retrieved from the Overpass
        (OpenStreetMaps) API.

        :param request: Current request, provided automatically.
        :returns: Serialized GeoJSON representation of all missing
            waters in the bounding box provided as URL parameters.
        """
        queryset: QuerySet = self.filter_queryset(self.get_queryset())
        # Get a list of all OSM IDs that are already present in the
        # database. This will be used later to filter the Overpass
        # results.
        osm_ids: List[int] = list(queryset.values_list("osm_id", flat=True))
        # Construct a filter set and retrieve the GeoLookupValue
        # object from the current request.
        geo_lookup_value: GeoLookupValue = self._get_geo_lookup_value(request)
        # Construct the Overpass query using the GeoLookupValue
        # bounding box.
        overpass_query: str = self.get_overpass_query(
            geo_lookup_value.get_bbox_coordinates()
        )
        # Query the Overpass API
        result: overpy.Result = self.client.query(overpass_query)
        waters: List[Water]

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

    @property
    def client(self) -> overpy.Overpass:
        """Returns the Overpass API client.

        :returns: Overpy instance, optionally with a custom server. The
            server can be set using the ``OVERPASS_SERVER`` setting.
        :rtype: overpy.Overpass
        """
        if hasattr(self, "_client"):
            return getattr(self, "_client")
        client = overpy.Overpass(url=getattr(settings, "OVERPASS_SERVER", None))
        setattr(self, "_client", client)
        return client

    @classmethod
    def _get_waters(
        cls,
        result: overpy.Result,
        osm_ids: List[int],
        *,
        commit: bool = True
    ) -> List[Water]:
        """Create waters for Overpass API result.

        :param result: Overpy query result.
        :type result: overpy.Result
        :param osm_ids: OSM IDs that should be ignored.
        :type osm_ids: list[int]
        :param commit: Whether to save the waters in the database.
        :type commit: bool
        :returns: List of all waters created
        """
        imported_ids: List[int] = osm_ids.copy()
        with transaction.atomic():
            for relation in result.get_relations():
                if relation.id in imported_ids:
                    # Do not import relation
                    continue
                name: str = cls.get_tagged_water_name(relation)
                osm_id: int = relation.id
                ways: List[LineString] = [
                    LineString([(geom.lon, geom.lat) for geom in member.geometry])
                    for member in relation.members
                    if isinstance(member, overpy.RelationWay)
                ]
                geometry = GeometryCollection(ways)
                water = Water(osm_id=osm_id, name=name, geometry=geometry)
                if commit:
                    water.save()
                imported_ids.append(osm_id)
                yield water
            for way in result.get_ways():
                if way.id in imported_ids:
                    # Do not import way
                    continue
                name: str = cls.get_tagged_water_name(way)
                osm_id: int = way.id
                geometry = GeometryCollection([
                    LineString([(geom.lon, geom.lat) for geom in way.geometry])
                ])

    @classmethod
    def get_tagged_water_name(cls, element: overpy.Element) -> str:
        """Retrieve human-readable name for an :class:`overpy.Element`
        instance.

        :param element: A relation, way or node instance.
        :type element: overpy.Element
        :returns: The name of the water.
        :rtype: str
        """
        # Use german name first
        name: str = element.tags.get("name:de")
        if name is None:
            # Fall back to default international name
            name = element.tags.get("name", None)
        if name is None:
            # Fall back to unnamed water based on its type
            water_type: str = element.tags.get("water", None)
            if water_type is None:
                # `water` tag not present, use `waterway` tag
                water_type = element.tags.get("waterway")
            if water_type is None:
                # No `water*` tag present, use `natural` tag
                water_type = element.tags.get("natural")
            name = cls.unnamed_waters.get(water_type, cls.default_water_name)
        return name

    @staticmethod
    def get_overpass_query(bbox: Tuple[float, float, float, float]) -> str:
        """Construct an Overpass query using its query language.

        :param bbox: Tuple of coordinates used for bounding box corners.
        :type bbox: tuple[float, float, float, float]
        :returns: String query for Overpass.
        :rtype: str
        """
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
