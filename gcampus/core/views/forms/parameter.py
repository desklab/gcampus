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

from __future__ import annotations

__all__ = ["ChemicalParameterFormSetView", "BiologicalParameterFormSetView"]

from typing import Optional

from django.http import HttpResponseRedirect, HttpRequest, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin, View

from gcampus.auth.exceptions import UnauthenticatedError, TokenEditPermissionError
from gcampus.auth.models.token import BaseToken
from gcampus.core.decorators import require_permission_edit_measurement
from gcampus.core.forms.measurement import (
    ChemicalParameterFormSet,
    BiologicalParameterFormSet,
    BaseParameterFormset,
)
from gcampus.core.models import Measurement
from gcampus.core.models.water import FlowType
from gcampus.core.views.forms.tabs import MeasurementEditTabsMixin


class BaseParameterFormSetView(MeasurementEditTabsMixin, TemplateResponseMixin, View):
    formset_class = BaseParameterFormset
    next_view_name: str

    def __init__(self, **kwargs):
        super(BaseParameterFormSetView, self).__init__(**kwargs)
        self.instance: Optional[Measurement] = None
        self.token: Optional[BaseToken] = None

    @method_decorator(require_permission_edit_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse(self.next_view_name, kwargs={"pk": self.instance.pk})

    def get(self, request: HttpRequest, pk: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, pk)
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_context_data(self, **kwargs):
        kwargs.setdefault("object", self.instance)
        kwargs.setdefault("measurement", self._get_measurement())
        return super().get_context_data(**kwargs)

    def get_instance(self, pk: int) -> Measurement:
        return get_object_or_404(Measurement, id=pk)

    def get_formset(self, request: HttpRequest, pk: int) -> formset_class:
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
        :param pk: This information comes from the URL and
            contains the ID to the measurement entry that is being
            edited.
        """
        self.instance = self.get_instance(pk)
        self.token: BaseToken = request.token
        if not self.token:
            raise UnauthenticatedError()
        if not self.token.has_perm("gcampuscore.change_measurement", obj=self.instance):
            raise TokenEditPermissionError()
        parameter_perms = [
            "gcampuscore.add_parameter",
            "gcampuscore.change_parameter",
            "gcampuscore.delete_parameter",
        ]
        if not self.token.has_perms(parameter_perms):
            raise TokenEditPermissionError()
        if request.method == "POST":
            return self.formset_class(
                data=request.POST, files=request.FILES, instance=self.instance
            )
        else:
            return self.formset_class(instance=self.instance)

    def form_valid(self, formset: formset_class):
        formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request: HttpRequest, pk: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, pk)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.render_to_response(self.get_context_data(formset=formset))


class ChemicalParameterFormSetView(BaseParameterFormSetView):
    formset_class = ChemicalParameterFormSet
    next_view_name = "gcampuscore:measurement-detail"
    current_tab_name = "chemical"
    template_name = "gcampuscore/forms/parameters-chemical.html"

    def get_success_url(self):
        # Depending on the flow type of the current water, additional
        # forms are possible. The next view is changed accordingly.
        if self._get_flow_type() == FlowType.RUNNING:
            self.next_view_name = "gcampuscore:edit-biological-parameters"
        return super(ChemicalParameterFormSetView, self).get_success_url()


class BiologicalParameterFormSetView(BaseParameterFormSetView):
    formset_class = BiologicalParameterFormSet
    current_tab_name = "biological"
    template_name = "gcampuscore/forms/parameters-biological.html"
    next_view_name = "gcampuscore:edit-structure-index"

    def get_instance(self, pk: int) -> Measurement:
        # Get the measurement to check the flow type of its related
        # water
        instance: Measurement = super().get_instance(pk)
        if instance.water.flow_type != FlowType.RUNNING:
            # Biological parameters are only supported by running flow
            # types.
            raise Http404("Parameter types not supported")
        return instance
