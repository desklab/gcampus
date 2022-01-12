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
    "PersonalMeasurementListView",
    "CourseMeasurementListView",
]

from typing import Optional

from django.utils.decorators import method_decorator
from django.views.generic import ListView

from gcampus.auth import session
from gcampus.auth.decorators import require_access_key, require_any_token
from gcampus.auth.models.token import CourseToken, TokenType
from gcampus.core.filters import MeasurementFilter
from gcampus.core.models import Measurement


class MeasurementListView(ListView):
    template_name = "gcampuscore/sites/list/measurement_list.html"
    model = Measurement
    context_object_name = "measurement_list"
    paginate_by = 10

    def __init__(self, *args, **kwargs):
        self.filter: Optional[MeasurementFilter] = None
        super(MeasurementListView, self).__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.filter = MeasurementFilter(
            self.request.GET, queryset=Measurement.objects.all()
        )
        return super(MeasurementListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.filter.qs
        return super(MeasurementListView, self).get_queryset()

    def get_context_data(self, *, object_list=None, **kwargs):
        if "filter" not in kwargs:
            kwargs["filter"] = self.filter
        return super(MeasurementListView, self).get_context_data(
            object_list=object_list, **kwargs
        )


class PersonalMeasurementListView(ListView):
    template_name = "gcampuscore/sites/list/personal_measurement_list.html"
    model = Measurement
    paginate_by = 10

    @method_decorator(require_access_key)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        token = session.get_token(self.request)
        self.queryset = Measurement.objects.filter(token__token=token)
        return super().get_queryset()


class CourseMeasurementListView(ListView):
    template_name = "gcampuscore/sites/list/course_measurement_list.html"
    model = Measurement
    paginate_by = 10

    @method_decorator(require_any_token)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        token: str = session.get_token(self.request)
        token_type: TokenType = session.get_token_type(self.request)
        if token_type is not TokenType.course_token:
            course_token: str = CourseToken.objects.get(access_keys__token=token).token
        else:
            course_token: str = token
        self.queryset = Measurement.all_objects.filter(
            token__parent_token__token=course_token
        )
        return super().get_queryset()
