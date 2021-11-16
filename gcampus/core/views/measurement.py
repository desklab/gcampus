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

from __future__ import annotations

from django.core.exceptions import (
    PermissionDenied,
    BadRequest,
)
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from gcampus.auth import utils, exceptions
from gcampus.auth.models.token import (
    COURSE_TOKEN_TYPE,
    CourseToken,
)
from gcampus.core.decorators import (
    require_permission_create_measurement,
    require_permission_edit_measurement
)
from gcampus.core.filters import MeasurementFilter
from gcampus.core.forms.measurement import MeasurementForm, TOKEN_FIELD_NAME
from gcampus.core.models import Measurement
from gcampus.core.views.base import TitleMixin


class MeasurementListView(ListView):
    template_name = "gcampuscore/sites/list/measurement_list.html"
    model = Measurement
    context_object_name = "measurement_list"
    paginate_by = 10
    queryset = Measurement.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = MeasurementFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context


class PersonalMeasurementListView(ListView):
    template_name = "gcampuscore/sites/list/personal_measurement_list.html"
    model = Measurement
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        token = utils.get_token(self.request)
        if token is None:
            raise PermissionDenied(exceptions.TOKEN_EMPTY_ERROR)
        personal_measurements = Measurement.objects.filter(token__token=token)
        return super().get_context_data(object_list=personal_measurements, **kwargs)


class CourseMeasurementListView(ListView):
    template_name = "gcampuscore/sites/list/course_measurement_list.html"
    model = Measurement
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        # Check if a token is provided
        token = utils.get_token(self.request)
        if token is None:
            raise PermissionDenied(exceptions.TOKEN_EMPTY_ERROR)
        # TODO: We might want to check whether the provided token exists
        #   and whether or not it is disabled. If it does not exists,
        #   the page will just be empty which is also ok.
        token_type = utils.get_token_type(self.request)
        if token_type != COURSE_TOKEN_TYPE:
            course_token = CourseToken.objects.get(accesskey__token=token).token
        else:
            course_token = token
        course_measurements = Measurement.objects.filter(
            token__parent_token__token=course_token
        )
        return super().get_context_data(object_list=course_measurements, **kwargs)


class MeasurementDetailView(DetailView):
    model = Measurement
    template_name = "gcampuscore/sites/detail/measurement_detail.html"


class MeasurementMapView(ListView):
    model = Measurement
    template_name = "gcampuscore/sites/mapview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = MeasurementFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context


class MeasurementCreateView(CreateView):
    form_class = MeasurementForm
    title = _("Create new Measurement")
    template_name = "gcampuscore/forms/measurement.html"
    next_view_name = "gcampuscore:add_parameters"

    @method_decorator(require_permission_create_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form: MeasurementForm):
        form_token = form.cleaned_data[TOKEN_FIELD_NAME]
        session_token = utils.get_token(self.request)
        if form_token != session_token:
            # Someone modified the session or token provided by the form
            raise BadRequest()
        return super(MeasurementCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.next_view_name, kwargs={"measurement_id": self.object.id})


class MeasurementEditView(TitleMixin, UpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = "gcampuscore/forms/measurement.html"

    def get_title(self) -> str:
        return _("Edit Measurement {pk:d} - Information").format(pk=self.object.pk)

    @method_decorator(require_permission_edit_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class HiddenCourseMeasurementListView(ListView):
    template_name = "gcampuscore/sites/list/hidden_course_measurement_list.html"
    model = Measurement
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        # Check if a token is provided
        token = utils.get_token(self.request)
        if token is None:
            raise PermissionDenied(exceptions.TOKEN_EMPTY_ERROR)
        # Check if provided token is actually a course token
        token_type = utils.get_token_type(self.request)
        if token_type != COURSE_TOKEN_TYPE:
            raise PermissionDenied(exceptions.TOKEN_INVALID_ERROR)
        course_measurements = Measurement.all_objects.filter(
            token__parent_token__token=token, hidden=True
        )
        return super().get_context_data(object_list=course_measurements, **kwargs)
