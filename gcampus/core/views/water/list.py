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

__all__ = [
    "WaterListView",
]

from django.db.models import Count
from django.utils.translation import gettext_lazy
from django.views.generic import ListView

from gcampus.core.models import Water
from gcampus.core.views.base import TitleMixin


class WaterListView(TitleMixin, ListView):
    template_name = "gcampuscore/sites/list/water_list.html"
    model = Water
    queryset = (
        Water.objects.filter(measurements__isnull=False)
        .distinct()
        .annotate(measurement_count=Count("measurements"))
        .defer("geometry")
    )
    title = gettext_lazy("All waters")
    context_object_name = "water_list"
    # paginate_by = 10
