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

__all__ = ["GeoLookupField"]

from numbers import Number
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.gis.forms import PointField, BaseGeometryWidget
from django.contrib.gis.geos import Point
from django.forms import MultiValueField, FloatField

from gcampus.api.utils import GeoLookupValue
from gcampus.api.widgets import GeoLookupWidget


class GeoLookupPointField(PointField):
    widget = BaseGeometryWidget


class GeoLookupField(MultiValueField):
    widget = GeoLookupWidget

    def __init__(self, fields=None, *args, **kwargs):
        if fields is None:
            max_size = getattr(settings, "MAX_GEOLOOKUP_BBOX_SIZE", 2000)
            fields = (
                GeoLookupPointField(required=True),
                FloatField(required=True, max_value=max_size),
            )
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list: Optional[Tuple[Point, Number]]):
        if data_list:
            return GeoLookupValue(*data_list)
        return None
