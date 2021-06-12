from __future__ import annotations

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic.edit import FormView

from gcampus.core.filters import MeasurementFilter
from gcampus.core.forms.measurement import MeasurementForm
from gcampus.core.models import Measurement
from gcampus.core.models.token import (
    can_token_create_measurement,
    TOKEN_CREATE_PERMISSION_ERROR,
)


class MeasurementListView(ListView):
    template_name = "gcampuscore/components/measurement_list.html"
    model = Measurement
    context_object_name = "measurement_list"
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = MeasurementFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context


class MeasurementDetailView(DetailView):
    model = Measurement
    template_name = "gcampuscore/components/measurement_detail.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["measurement_list"] = Measurement.objects.all()
        current_measurement = self.object
        point = Point(current_measurement.location.coords)
        close_measurements = Measurement.objects.filter(
            location__distance_lte=(point, Distance(km=2))
        ).all()
        close_measurements = close_measurements.exclude(pk=self.object.pk)
        context["close_measurements"] = close_measurements
        return context


class MeasurementMapView(ListView):
    model = Measurement
    template_name = "gcampuscore/components/mapview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = MeasurementFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context


class MeasurementFormView(FormView):
    template_name = "gcampuscore/forms/measurement.html"
    form_class = MeasurementForm
    next_view_name = "gcampuscore:add_data_points"

    def get(self, request, *args, **kwargs):
        token = request.session.get("token", None)
        if can_token_create_measurement(token):
            return super(MeasurementFormView, self).get(request, *args, **kwargs)
        else:
            raise PermissionDenied(TOKEN_CREATE_PERMISSION_ERROR)

    def post(self, request, *args, **kwargs):
        token = request.session.get("token", None)
        if can_token_create_measurement(token):
            return super(MeasurementFormView, self).post(request, *args, **kwargs)
        else:
            raise PermissionDenied(TOKEN_CREATE_PERMISSION_ERROR)

    def form_valid(self, form: MeasurementForm):
        instance: Measurement = form.save()
        return HttpResponseRedirect(self.get_next_url(instance))

    def get_next_url(self, instance: Measurement):
        return reverse(self.next_view_name, kwargs={"measurement_id": instance.id})
