from __future__ import annotations

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView, View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormView

from gcampus.core.filters import MeasurementFilter
from gcampus.core.forms.measurement import MeasurementForm, DataPointFormSet
from gcampus.core.models import Measurement
from gcampus.core.models.token import can_token_create_measurement, \
    TOKEN_CREATE_PERMISSION_ERROR


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
        token = self.request.session["token"]
        instance: Measurement = form.save()
        return HttpResponseRedirect(self.get_next_url(instance))

    def get_next_url(self, instance: Measurement):
        return reverse(self.next_view_name, kwargs={"measurement_id": instance.id})


class DataPointFormSetView(TemplateResponseMixin, View):
    formset_class = DataPointFormSet
    template_name = "gcampuscore/forms/datapoints.html"
    next_view_name = "gcampuscore:measurement_detail"

    def form_valid(self, formset: DataPointFormSet, measurement_id):
        token = self.request.session["token"]
        formset.save()
        return HttpResponseRedirect(self.get_next_url(measurement_id))

    def get_next_url(self, measurement_id):
        return reverse(self.next_view_name, kwargs={"pk": measurement_id})

    def get_formset(
        self, request: HttpRequest, measurement_id: int
    ) -> DataPointFormSetView.formset_class:
        """Get Formset

        Get the formset for the current request based on the instance of
        the specified measurement ID.
        Will raise a 404 error if no measurement with such ID exists.

        :param request: The request object. Contains e.g. the POST form
            data.
        :param measurement_id: This information comes from the URL and
            contains the ID to the measurement entry that is being
            edited.
        """
        instance: Measurement = get_object_or_404(Measurement, id=measurement_id)
        if request.method == "POST":
            return self.formset_class(
                data=request.POST, files=request.FILES, instance=instance
            )
        else:
            return self.formset_class(instance=instance)

    def post(self, request: HttpRequest, measurement_id: int, *args, **kwargs):
        token = request.session.get("token", None)
        if not can_token_create_measurement(token):
            raise PermissionDenied(TOKEN_CREATE_PERMISSION_ERROR)
        formset = self.get_formset(request, measurement_id)
        if formset.is_valid():
            return self.form_valid(formset, measurement_id)
        else:
            return self.render_to_response({"formset": formset})

    def get(self, request: HttpRequest, measurement_id: int, *args, **kwargs):
        token = request.session.get("token", None)
        if not can_token_create_measurement(token):
            raise PermissionDenied(TOKEN_CREATE_PERMISSION_ERROR)
        formset = self.get_formset(request, measurement_id)
        return self.render_to_response({"formset": formset})
