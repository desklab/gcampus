from numbers import Number
from typing import Tuple, Union

import coreschema
import overpy
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy
from django.views.decorators.cache import cache_page
from overpy.exception import OverpassTooManyRequests
from rest_framework.decorators import action
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from rest_framework import viewsets, serializers, status
from rest_framework.exceptions import ParseError, Throttled
from rest_framework.request import Request
from rest_framework.response import Response

from gcampus.api.serializers import GeoLookupSerializer


class GeoLookupViewSet(viewsets.ViewSet):
    api = overpy.Overpass()
    serializer = GeoLookupSerializer

    @method_decorator(cache_page(60 * 60 * 24 * 2))  # Cache for two days
    def list(self, request: Request, **kwargs):
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
        center = Point(x, y, srid=srid)
        query = self._get_overpass_query(center, size)
        try:
            result = self.api.query(query)
        except OverpassTooManyRequests:
            raise Throttled
        serializer = self.serializer()
        return Response(
            serializer.to_representation(result.get_ways()), status=status.HTTP_200_OK
        )

    def _get_overpass_query(self, center: Point, size: Union[Number, Distance]) -> str:
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
        (
            way["natural"="water"]({bbox});
            way["waterway"]({bbox});
            way["water"]({bbox});
        );
        out body;
        >;
        out skel qt;
        """
        return query


def get_bbox_coordinates(
        center: Point, size: Union[Number, Distance]
) -> Tuple[Point, Point]:
    """Get Bounding Box Coordinates

    Get the coordinates (two points at the corners) describing a square
    bounding box of size ``size``, located at ``center``.
    To easily easily calculate the position of these corners relative to
    the center point, the coordinate system is transformed into
    EPSG:3857 WGS 84, a coordinate system that uses meters instead of
    longitude and latitude. The points that are returned will be
    transformed back to the original coordinate system. If the center
    point has no specified coordinate system (i.e. srid == None), an
    srid of 4326 (EPSG:4326 WGS 84) is assumed as a sensible default.

    :param center: The center point
    :param size: The square edge size. If size is a number (e.g. ``int``
        or ``float``), the unit will be meters. The parameter can also
        be of type Distance to easily convert between different units.
    :return: Tuple of two points describing the square bounding box
    :rtype: Tuple[Point, Point]
    """
    if isinstance(size, Distance):
        size = size["m"]
    elif not isinstance(size, Number):
        raise ValueError(
            "Unexpected type for argument 'size'. Expected any"
            f" number or Distance but got {type(size)}."
        )
    if center.srid is None:
        center.srid = 4326  # default coordinate system
    if center.srid != 3857:
        center_meter: Point = center.clone()
        # Transform longitude and latitude in meters
        center_meter.transform(3857)
    else:
        center_meter: Point = center.clone()
    edge = size / 2
    upper_left = Point(center_meter.x - edge, center_meter.y - edge, srid=3857)
    lower_right = Point(center_meter.x + edge, center_meter.y + edge, srid=3857)
    # Transform back to default coordinate system (longitude, latitude)
    upper_left.transform(center.srid)
    lower_right.transform(center.srid)
    return upper_left, lower_right
