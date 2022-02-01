#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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

from datetime import datetime
from typing import Optional

from django.utils import timezone
from django.views.generic import ListView

from gcampus.core.filters import MeasurementFilter
from gcampus.core.models import Measurement

from gcampus.core.util import get_weeks_from_today, convert_dates_to_js_milliseconds


class MeasurementListView(ListView):
    template_name = "gcampuscore/sites/list/measurement_list.html"
    model = Measurement
    context_object_name = "measurement_list"

    # paginate_by = 10

    def __init__(self, *args, **kwargs):
        self.filter: Optional[MeasurementFilter] = None
        super(MeasurementListView, self).__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.filter = MeasurementFilter(
            self.request.GET, queryset=Measurement.objects.all(),
            request=self.request)
        return super(MeasurementListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.filter.qs
        return super(MeasurementListView, self).get_queryset()

    def get_context_data(self, *, object_list=None, **kwargs):
        if "filter" not in kwargs:
            kwargs["filter"] = self.filter
        kwargs["today"] = timezone.now()
        earliest_date: datetime = Measurement.objects.values_list("time", flat=True).earliest("time")
        week_list = get_weeks_from_today(earliest_date)
        kwargs["week_list_js"] = convert_dates_to_js_milliseconds(week_list)
        return super(MeasurementListView, self).get_context_data(
            object_list=object_list, **kwargs
        )
