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

from typing import Optional

from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import ModelFormMixin, UpdateView

from gcampus.auth.exceptions import UnauthenticatedError, TokenEditPermissionError
from gcampus.auth.models.token import BaseToken
from gcampus.core.decorators import require_permission_edit_measurement
from gcampus.core.forms.measurement import (
    ChemicalParameterFormSet,
    BiologicalParameterFormSet,
    StructureIndexForm,
)
from gcampus.core.models import Parameter, Measurement
from gcampus.core.models.index.structure import StructureIndex
from gcampus.core.views.base import TitleMixin


class ChemicalParameterFormSetView(TitleMixin, TemplateResponseMixin, View):
    formset_class = ChemicalParameterFormSet
    template_name = "gcampuscore/forms/parameters-chemical.html"

    def get_title(self) -> str:
        return _("Edit Measurement {pk:d} - Chemical Parameters").format(
            pk=self.instance.pk
        )

    def get_next_url(self):
        if self.instance.water.flow_type == "running":
            next_view_name = "gcampuscore:edit-biological-parameters"
        elif self.instance.water.flow_type == "standing":
            next_view_name = "gcampuscore:measurement-detail"
        else:
            next_view_name = "gcampuscore:measurement-detail"
        return reverse(next_view_name, kwargs={"pk": self.instance.pk})

    def get_context_data(self, **kwargs):
        if "object" not in kwargs:
            kwargs["object"] = self.instance
        return super().get_context_data(**kwargs)

    def __init__(self, **kwargs):
        super(ChemicalParameterFormSetView, self).__init__(**kwargs)
        self.instance: Optional[Parameter] = None
        self.token: Optional[BaseToken] = None

    def form_valid(self, formset: ChemicalParameterFormSet):
        formset.save()
        return HttpResponseRedirect(self.get_next_url())

    def get_formset(
        self, request: HttpRequest, pk: int
    ) -> ChemicalParameterFormSetView.formset_class:
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
        self.instance = get_object_or_404(Measurement, id=pk)
        self.token: BaseToken = request.token
        if self.token is None:
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

    def post(self, request: HttpRequest, pk: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, pk)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.render_to_response(self.get_context_data(formset=formset))

    def get(self, request: HttpRequest, pk: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, pk)
        return self.render_to_response(self.get_context_data(formset=formset))


class BiologicalParameterFormSetView(TitleMixin, TemplateResponseMixin, View):
    formset_class = BiologicalParameterFormSet
    template_name = "gcampuscore/forms/parameters-biological.html"
    next_view_name = "gcampuscore:edit-structure-index"

    def get_title(self) -> str:
        return _("Edit Measurement {pk:d} - Biological Parameters").format(
            pk=self.instance.pk
        )

    def get_next_url(self):
        return reverse(self.next_view_name, kwargs={"pk": self.instance.pk})

    def get_context_data(self, **kwargs):
        if "object" not in kwargs:
            kwargs["object"] = self.instance
        return super().get_context_data(**kwargs)

    def __init__(self, **kwargs):
        super(BiologicalParameterFormSetView, self).__init__(**kwargs)
        self.instance: Optional[Parameter] = None
        self.token: Optional[BaseToken] = None

    def form_valid(self, formset: BiologicalParameterFormSet):
        formset.save()
        return HttpResponseRedirect(self.get_next_url())

    def get_formset(
        self, request: HttpRequest, pk: int
    ) -> BiologicalParameterFormSetView.formset_class:
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
        self.instance = get_object_or_404(Measurement, id=pk)
        self.token: BaseToken = request.token
        if self.token is None:
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

    def post(self, request: HttpRequest, pk: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, pk)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.render_to_response(self.get_context_data(formset=formset))

    def get(self, request: HttpRequest, pk: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, pk)
        return self.render_to_response(self.get_context_data(formset=formset))


class StructureIndexFormViewMixin(TitleMixin, ModelFormMixin):
    template_name = "gcampuscore/forms/structure-index.html"
    next_view_name = "gcampuscore:measurement-detail"

    def get_success_url(self):
        return reverse(self.next_view_name, kwargs={"pk": self.object.pk})


class StructureIndexEditView(StructureIndexFormViewMixin, UpdateView):
    model = StructureIndex
    form_class = StructureIndexForm

    @method_decorator(require_permission_edit_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_title(self) -> str:
        return gettext("Edit Measurement {pk:d} - Structure Index").format(
            pk=self.object.pk
        )
