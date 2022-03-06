#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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

from numbers import Number
from typing import Tuple, Union, List

import overpy
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from overpy.exception import OverpassTooManyRequests, OverpassGatewayTimeout
from rest_framework import viewsets, serializers, status
from rest_framework.exceptions import ParseError, Throttled
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from gcampus.api.serializers import GeoLookupSerializer
from gcampus.api.utils import get_bbox_coordinates


class GeoLookupViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    api = overpy.Overpass(url=getattr(settings, "OVERPASS_SERVER", None))
    serializer = GeoLookupSerializer

    # Cache for two days by default
    @method_decorator(cache_page(getattr(settings, "OVERPASS_CACHE", 60 * 60 * 24 * 2)))
    def list(self, request: Request, **kwargs):  # noqa
        params = request.query_params
        coordinates = params.get("coords", None)
        size = params.get("size", None)
        srid = params.get("srid", 4326)
        if coordinates is None:
            raise serializers.ValidationError("'coords' parameter is required")
        if size is None:
            raise serializers.ValidationError("'size' parameter is required")
        try:
            x, y = str(coordinates).split(",")
            x = float(x)
            y = float(y)
        except (TypeError, ValueError, OverflowError):
            raise ParseError("Unable to parse 'coords'")
        try:
            size = float(size)
        except (TypeError, ValueError, OverflowError):
            raise ParseError("Unable to parse 'size'")
        # Generate the overpass query
        center = Point(x, y, srid=srid)
        query = self._get_overpass_query(center, size)
        # Query the overpass api
        try:
            result = self.api.query(query)
        except (OverpassTooManyRequests, OverpassGatewayTimeout):
            raise Throttled()

        # Get all relations from the result and save the ID of each
        # way contained in the relation. All ways that are part of an
        # relation will be discarded later.
        relations: List[overpy.Relation] = result.get_relations()
        relation_way_ids: List[overpy.RelationWay] = []
        for relation in relations:
            for member in relation.members:
                if isinstance(member, overpy.RelationWay):
                    relation_way_ids.append(member.ref)
        # Only include the ways that are unique and not in a relation
        # from the result
        ways: List[overpy.Way] = [
            way for way in result.get_ways() if way.id not in relation_way_ids
        ]
        # Combine both lists of all relations and ways which are not
        # part of any relation
        instances: List[Union[overpy.Way, overpy.Relation]] = relations + ways
        del relation_way_ids
        serializer = self.serializer()
        return Response(
            serializer.to_representation(instances), status=status.HTTP_200_OK
        )

    @staticmethod
    def _get_overpass_query(center: Point, size: Union[Number, Distance]) -> str:
        """Get Overpass Query

        Generate the query for used for overpass

        :param center: The center point
        :param size: The square edge size. If size is a number (e.g. ``int``
            or ``float``), the unit will be meters. The parameter can also
            be of type Distance to easily convert between different units.
        :return: String used to query overpass
        :rtype: str
        """
        upper_left, lower_right = get_bbox_coordinates(center, size)
        bbox = f"{upper_left.x},{upper_left.y},{lower_right.x},{lower_right.y}"
        query = f"""
        [bbox:{bbox}];
        (
            way["natural"="water"];>;
            relation["natural"="water"];>;
            way["waterway"];>;
            relation["waterway"];>;
        );
        // (._; >;);
        out geom;
        """
        return query

