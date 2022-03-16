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

__all__ = ["GeoLookupWidget"]

from typing import Optional

from django.contrib.gis.forms import BaseGeometryWidget
from django.forms import NumberInput
from django_filters.widgets import SuffixedMultiWidget

from gcampus.api.utils import GeoLookupValue


class GeoLookupWidget(SuffixedMultiWidget):
    suffixes = ["center", "size"]

    def __init__(self, attrs=None):
        widgets = (BaseGeometryWidget(), NumberInput())
        super().__init__(widgets, attrs)

    def decompress(self, value: Optional[GeoLookupValue]):
        if value:
            return [value.center, value.size]
        return [None, None]
