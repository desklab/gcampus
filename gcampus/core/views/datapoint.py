from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.base import TemplateResponseMixin, View

from gcampus.core.forms.measurement import DataPointFormSet
from gcampus.core.models import DataPoint, Measurement
from gcampus.core.models.token import (
    can_token_create_measurement,
    TOKEN_CREATE_PERMISSION_ERROR,
)


class DatapointDetailView(DetailView):
    model = DataPoint


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
