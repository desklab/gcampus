#  Copyright (C) 2021 desklab gUG
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

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.core.exceptions import (
    PermissionDenied,
    SuspiciousOperation,
    ObjectDoesNotExist,
    FieldError,
)
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from gcampus.auth import utils, exceptions
from gcampus.auth.exceptions import TOKEN_CREATE_PERMISSION_ERROR
from gcampus.auth.models.token import (
    can_token_create_measurement,
    COURSE_TOKEN_TYPE,
)
from gcampus.auth.utils import get_token
from gcampus.core.filters import MeasurementFilter
from gcampus.core.forms.measurement import MeasurementForm, TOKEN_FIELD_NAME
from gcampus.core.models import Measurement


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
        # Check if provided token is actually a course token
        token_type = utils.get_token_type(self.request)
        if token_type != COURSE_TOKEN_TYPE:
            raise PermissionDenied(exceptions.TOKEN_INVALID_ERROR)
        course_measurements = Measurement.objects.filter(
            token__parent_token__token=token
        )
        return super().get_context_data(object_list=course_measurements, **kwargs)


class MeasurementDetailView(DetailView):
    model = Measurement
    template_name = "gcampuscore/sites/detail/measurement_detail.html"


def hide(request, pk):
    measurement = Measurement.objects.filter(pk=pk)
    parent_token = get_token(request)
    if parent_token is not None and measurement:
        measurement_token = measurement[0].token.parent_token
        if measurement_token.token == parent_token:
            context = {"measurement": measurement[0]}
            measurement.update(hidden=True)
            return render(
                request, "gcampuscore/sites/detail/hidden_success.html", context
            )
        else:
            raise PermissionDenied(exceptions.TOKEN_INVALID_ERROR)
    else:
        if not measurement:
            raise ObjectDoesNotExist(_("The measurement is probably already hidden"))
        if not parent_token:
            raise PermissionDenied(exceptions.TOKEN_EMPTY_ERROR)


def show(request, pk):
    measurement = Measurement.all_objects.filter(pk=pk)
    parent_token = get_token(request)
    if parent_token is not None and measurement:
        if measurement[0].hidden == False:
            raise FieldError(_("Measurement is already public"))
        measurement_token = measurement[0].token.parent_token
        if measurement_token.token == parent_token:
            context = {"measurement": measurement[0]}
            measurement.update(hidden=False)
            return render(
                request, "gcampuscore/sites/detail/show_success.html", context
            )
        else:
            raise PermissionDenied(exceptions.TOKEN_INVALID_ERROR)
    else:
        if not measurement:
            raise ObjectDoesNotExist("The measurement is probably already public")
        if not parent_token:
            raise PermissionDenied(exceptions.TOKEN_EMPTY_ERROR)


class MeasurementMapView(ListView):
    model = Measurement
    template_name = "gcampuscore/sites/mapview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = MeasurementFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context


class MeasurementFormView(FormView):
    template_name = "gcampuscore/forms/measurement.html"
    form_class = MeasurementForm
    next_view_name = "gcampuscore:add_parameters"

    def get(self, request, *args, **kwargs):
        token = utils.get_token(request)
        token_type = utils.get_token_type(request)
        if can_token_create_measurement(token, token_type=token_type):
            return super(MeasurementFormView, self).get(request, *args, **kwargs)
        else:
            raise PermissionDenied(TOKEN_CREATE_PERMISSION_ERROR)

    def post(self, request, *args, **kwargs):
        token = utils.get_token(request)
        token_type = utils.get_token_type(request)
        if can_token_create_measurement(token, token_type=token_type):
            return super(MeasurementFormView, self).post(request, *args, **kwargs)
        else:
            raise PermissionDenied(TOKEN_CREATE_PERMISSION_ERROR)

    def form_valid(self, form: MeasurementForm):
        form_token = form.cleaned_data[TOKEN_FIELD_NAME]
        session_token = utils.get_token(self.request)
        if form_token != session_token:
            # Someone modified the session or token provided by the form
            raise SuspiciousOperation()
        instance: Measurement = form.save()
        return HttpResponseRedirect(self.get_next_url(instance))

    def get_next_url(self, instance: Measurement):
        return reverse(self.next_view_name, kwargs={"measurement_id": instance.id})


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
