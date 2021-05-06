from __future__ import annotations

from django.db.models import Q
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView, View
from django.views.generic.base import TemplateResponseMixin, TemplateView
from django.views.generic.edit import FormView

from gcampus.core.forms.measurement import MeasurementForm, DataPointFormSet
from gcampus.core.models import DataPoint
from gcampus.core.models import Measurement
from gcampus.core.filters import MeasurementFilter


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
            location__distance_lte=(point, Distance(km=2))).all()
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

    def form_valid(self, form: MeasurementForm):
        instance: Measurement = form.save()
        return HttpResponseRedirect(self.get_next_url(instance))

    def get_next_url(self, instance: Measurement):
        return reverse(self.next_view_name, kwargs={"measurement_id": instance.id})


class DataPointFormSetView(TemplateResponseMixin, View):
    formset_class = DataPointFormSet
    template_name = "gcampuscore/forms/datapoints.html"
    success_url = "/admin"

    def form_valid(self, formset: DataPointFormSet):
        formset.save()
        return HttpResponseRedirect(self.success_url)

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
        formset = self.get_formset(request, measurement_id)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.render_to_response({"formset": formset})

    def get(self, request: HttpRequest, measurement_id: int, *args, **kwargs):
        formset = self.get_formset(request, measurement_id)
        return self.render_to_response({"formset": formset})
