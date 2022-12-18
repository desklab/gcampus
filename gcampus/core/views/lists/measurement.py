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
    "MeasurementListView",
]

from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.views.generic import ListView

from gcampus.core.filters import MeasurementFilterSet
from gcampus.core.models import Measurement
from gcampus.core.views.base import TitleMixin


class MeasurementListView(TitleMixin, ListView):
    template_name = "gcampuscore/sites/list/measurement_list.html"
    model = Measurement
    queryset = (
        Measurement.objects.prefetch_related(
            "parameters__parameter_type",
            "bach_index",
            "saprobic_index",
            "structure_index",
            "trophic_index",
        )
        .select_related("water")
        .defer("water__geometry")
        .order_by("-time")
        .all()
    )
    title = gettext_lazy("All measurements")
    context_object_name = "measurement_list"
    filter: MeasurementFilterSet
    paginate_by = 10

    def get_queryset(self):
        if not hasattr(self, "filter"):
            self.filter = MeasurementFilterSet(
                self.request.GET, queryset=self.queryset, request=self.request
            )
        self.queryset = self.filter.qs
        return super(MeasurementListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "filter" not in context:
            context["filter"] = self.filter
        if "filter_status" not in context:
            context["filter_status"] = False
        context["today"] = timezone.now()
        context["filter_status"] = self.filter.get_status()
        context["count"] = context["paginator"].count
        return context
