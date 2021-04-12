from numbers import Number
from typing import Tuple, Union

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from rest_framework import viewsets


class GeoLookupViewSet(viewsets.ViewSet):
    pass


def get_bbox_coordinates(
    center: Point, size: Union[Number, Distance]
) -> Tuple[Point, ...]:
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
    :returns: Tuple of two points describing the square bounding box
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
    if center.srid is not 3857:
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
