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

__all__ = ["GeoLookupValue"]

from dataclasses import dataclass
from numbers import Number
from typing import Union

from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import Distance

from gcampus.api.views.functions import get_bbox_coordinates


@dataclass
class GeoLookupValue:
    center: Point
    size: Union[Number, Distance]

    def get_bbox_poly(self):
        top_left: Point
        bottom_right: Point
        top_left, bottom_right = get_bbox_coordinates(self.center, self.size)
        return Polygon.from_bbox(
            (top_left.x, top_left.y, bottom_right.x, bottom_right.y)
        )
