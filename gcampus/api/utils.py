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

__all__ = ["GeoLookupValue"]

from dataclasses import dataclass
from numbers import Number
from typing import Union, Tuple

from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import Distance


@dataclass(frozen=True, eq=True)
class GeoLookupValue:
    center: Point
    size: Union[Number, Distance]

    def get_bbox_poly(self):
        return Polygon.from_bbox(self.get_bbox_coordinates())

    def get_bbox_coordinates(self) -> Tuple[float, float, float, float]:
        """Get Bounding Box Coordinates

        Get the coordinates (two points at the corners) describing a square
        bounding box of size ``size``, located at ``center``.
        To easily calculate the position of these corners relative to
        the center point, the coordinate system is transformed into
        EPSG:3857 WGS 84, a coordinate system that uses meters instead of
        longitude and latitude. The points that are returned will be
        transformed back to the original coordinate system. If the center
        point has no specified coordinate system (i.e. srid == None), an
        srid of 4326 (EPSG:4326 WGS 84) is assumed as a sensible default.

        :return: Tuple of two points describing the square bounding box
        :rtype: Tuple[Point, Point]
        """
        if isinstance(self.size, Distance):
            size_meter = self.size["m"]
        elif isinstance(self.size, Number):
            size_meter = self.size
        else:
            raise ValueError(
                "Unexpected type for attribute 'size'. Expected any"
                f" number or Distance but got {type(self.size)}."
            )
        if self.center.srid is None:
            self.center.srid = 4326  # default coordinate system
        if self.center.srid != 3857:
            center_meter: Point = self.center.clone()
            # Transform longitude and latitude in meters
            center_meter.transform(3857)
        else:
            center_meter: Point = self.center.clone()
        edge = size_meter / 2
        upper_left = Point(center_meter.x - edge, center_meter.y - edge, srid=3857)
        lower_right = Point(center_meter.x + edge, center_meter.y + edge, srid=3857)
        # Transform back to default coordinate system (longitude, latitude)
        upper_left.transform(self.center.srid)
        lower_right.transform(self.center.srid)
        return upper_left.x, upper_left.y, lower_right.x, lower_right.y
