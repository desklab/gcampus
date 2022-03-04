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

__all__ = ["GeoLookupFilter"]

from typing import Optional

from django_filters import Filter

from gcampus.api.fields import GeoLookupField
from gcampus.api.utils import GeoLookupValue


class GeoLookupFilter(Filter):
    field_class = GeoLookupField
    lookup_expr = "intersects"

    def __init__(self, field_name=None, lookup_expr=None, **kwargs):
        if lookup_expr is None:
            lookup_expr = self.lookup_expr
        super(GeoLookupFilter, self).__init__(
            field_name=field_name, lookup_expr=lookup_expr, **kwargs
        )

    def filter(self, qs, value: Optional[GeoLookupValue]):
        if value:
            bbox = value.get_bbox_poly()
            return qs.filter(geometry__intersects=bbox)
        return qs
