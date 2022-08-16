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

__all__ = ["WaterLookupFilterSet", "MeasurementFilter"]

from django_filters.rest_framework import FilterSet, ModelMultipleChoiceFilter

from gcampus.api.filters import GeoLookupFilter
from gcampus.core.models import Water


class WaterLookupFilterSet(FilterSet):
    geo = GeoLookupFilter(field_name="geometry", required=True)


class MeasurementFilter(FilterSet):
    water = ModelMultipleChoiceFilter(
        field_name="water_id", queryset=Water.objects.all()
    )
