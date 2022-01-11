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
)
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from gcampus.auth import utils, exceptions
from gcampus.auth.fields.token import check_form_and_request_token
from gcampus.auth.models.token import (
    COURSE_TOKEN_TYPE,
    can_token_edit_measurement,
)
from gcampus.auth.utils import is_authenticated, get_token, get_token_type
from gcampus.core.decorators import (
    require_permission_create_measurement,
    require_permission_edit_measurement,
)
from gcampus.core.filters import MeasurementFilter
from gcampus.core.forms.measurement import MeasurementForm
from gcampus.core.models import Measurement
from gcampus.core.views.base import TitleMixin
from gcampus.core.views.measurement.list import (
    MeasurementListView,
)


class MeasurementDetailView(TitleMixin, DetailView):
    model = Measurement
    queryset = Measurement.objects
    template_name = "gcampuscore/sites/detail/measurement_detail.html"

    def get_context_data(self, **kwargs):
        if is_authenticated(self.request) and self.object:
            token = get_token(self.request)
            token_type = get_token_type(self.request)
            if can_token_edit_measurement(token, self.object, token_type=token_type):
                # Measurement can be edited by the current user
                # Create an empty form from the MeasurementDeleteView
                # to display a delete button.
                kwargs["can_edit"] = True
                delete_form = MeasurementDeleteView.form_class()
                kwargs["delete_form"] = delete_form
        return super(MeasurementDetailView, self).get_context_data(**kwargs)

    def get_title(self) -> str:
        if self.object:
            return str(self.object)
        else:
            raise RuntimeError("'self.object' is not set")


class MeasurementMapView(ListView):
    model = Measurement
    template_name = "gcampuscore/sites/mapview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = MeasurementFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context


class MeasurementCreateView(TitleMixin, CreateView):
    form_class = MeasurementForm
    title = _("Create new measurement")
    template_name = "gcampuscore/forms/measurement.html"
    next_view_name = "gcampuscore:add-parameters"

    @method_decorator(require_permission_create_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form: MeasurementForm):
        check_form_and_request_token(form, self.request)
        return super(MeasurementCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.next_view_name, kwargs={"pk": self.object.id})


class MeasurementEditView(TitleMixin, UpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = "gcampuscore/forms/measurement.html"

    def form_valid(self, form: MeasurementForm):
        check_form_and_request_token(form, self.request)
        return super(MeasurementEditView, self).form_valid(form)

    def get_title(self) -> str:
        return _("Edit Measurement {pk:d} - Information").format(pk=self.object.pk)

    @method_decorator(require_permission_edit_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class MeasurementDeleteView(TitleMixin, DeleteView):
    model = Measurement
    success_url = reverse_lazy("gcampuscore:mapview")

    # Only allow post requests. HTML frontend is handled by
    # MeasurementDetailView. See MeasurementDetailView.get_context_data.
    @method_decorator(require_POST)
    @method_decorator(require_permission_edit_measurement)
    def dispatch(self, request, pk: int, *args, **kwargs):
        return super(MeasurementDeleteView, self).dispatch(request, pk, *args, **kwargs)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object: Measurement
        # Instead of permanently deleting the measurement, it is instead
        # hidden from all users. Consider this as some kind of temporary
        # trash (i.e. marked for deletion).
        self.object.hidden = True
        self.object.save()
        return redirect(success_url)
