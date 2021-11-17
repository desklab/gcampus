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

from typing import Optional

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateResponseMixin, View

from gcampus.auth import utils
from gcampus.auth.exceptions import TOKEN_EDIT_PERMISSION_ERROR
from gcampus.auth.fields.token import HIDDEN_TOKEN_FIELD_NAME, \
    check_form_and_request_token
from gcampus.auth.models.token import can_token_edit_measurement
from gcampus.core.forms.measurement import ParameterFormSet
from gcampus.core.models import Parameter, Measurement
from gcampus.core.views.base import TitleMixin


class ParameterFormSetView(TitleMixin, TemplateResponseMixin, View):
    formset_class = ParameterFormSet
    template_name = "gcampuscore/forms/parameters.html"
    next_view_name = "gcampuscore:measurement_detail"

    def get_title(self) -> str:
        return _("Edit Measurement {pk:d} - Measured Parameters").format(
            pk=self.instance.pk
        )

    def get_context_data(self, **kwargs):
        if "object" not in kwargs:
            kwargs["object"] = self.instance
        return super().get_context_data(**kwargs)

    def __init__(self, **kwargs):
        super(ParameterFormSetView, self).__init__(**kwargs)
        self.instance: Optional[Parameter] = None

    def form_valid(self, formset: ParameterFormSet, measurement_id):
        formset.save()
        return HttpResponseRedirect(self.get_next_url(measurement_id))

    def get_next_url(self, pk):
        return reverse(self.next_view_name, kwargs={"pk": pk})

    def get_formset(
        self, request: HttpRequest, pk: int
    ) -> ParameterFormSetView.formset_class:
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

    def post(self, request: HttpRequest, pk: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, pk)
        if formset.is_valid():
            check_form_and_request_token(formset.management_form, self.request)
            return self.form_valid(formset, pk)
        else:
            return self.render_to_response(self.get_context_data(formset=formset))

    def get(self, request: HttpRequest, pk: int, *args, **kwargs):
        # This will raise an exception if the provided token has
        # insufficient permissions
        formset = self.get_formset(request, pk)
        return self.render_to_response(self.get_context_data(formset=formset))
