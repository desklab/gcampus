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

from typing import Optional

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.base import TemplateResponseMixin, View

from gcampus.auth import utils
from gcampus.auth.exceptions import TOKEN_EDIT_PERMISSION_ERROR
from gcampus.auth.models.token import can_token_edit_measurement
from gcampus.core.forms.measurement import DataPointFormSet, TOKEN_FIELD_NAME
from gcampus.core.models import DataPoint, Measurement


class DatapointDetailView(DetailView):
    model = DataPoint


class DataPointFormSetView(TemplateResponseMixin, View):
    formset_class = DataPointFormSet
    template_name = "gcampuscore/forms/datapoints.html"
    next_view_name = "gcampuscore:measurement_detail"

    def __init__(self, **kwargs):
        super(DataPointFormSetView, self).__init__(**kwargs)
        self.instance: Optional[DataPoint] = None

    def form_valid(self, formset: DataPointFormSet, measurement_id):
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
        This method will also check whether the provided token (taken
        from the session), is valid and allowed to edit a measurement.
        Otherwise, a :class:`django.core.exceptions.PermissionDenied`
        exception is raised.

        :param request: The request object. Contains e.g. the POST form
            data.
        :param measurement_id: This information comes from the URL and
            contains the ID to the measurement entry that is being
            edited.
        """
        self.instance = get_object_or_404(Measurement, id=measurement_id)
        token = utils.get_token(request)
        token_type = utils.get_token_type(request)
        if not can_token_edit_measurement(token, self.instance, token_type=token_type):
            raise PermissionDenied(TOKEN_EDIT_PERMISSION_ERROR)
        if request.method == "POST":
            return self.formset_class(
                data=request.POST, files=request.FILES, instance=self.instance
            )
        else:
            return self.formset_class(instance=self.instance)

    def post(self, request: HttpRequest, measurement_id: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, measurement_id)
        if formset.is_valid():
            form_token = formset.management_form.cleaned_data[TOKEN_FIELD_NAME]
            session_token = utils.get_token(request)
            if form_token != session_token:
                # Someone modified the session or token provided by the
                # form
                raise SuspiciousOperation()
            return self.form_valid(formset, measurement_id)
        else:
            return self.render_to_response({"formset": formset})

    def get(self, request: HttpRequest, measurement_id: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, measurement_id)
        return self.render_to_response({"formset": formset})
