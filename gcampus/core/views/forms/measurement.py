#  Copyright (C) 2022 desklab gUG (haftungsbeschränkt)
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

__all__ = [
    "MeasurementDeleteView",
    "MeasurementCreateView",
    "MeasurementEditView",
]

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy, gettext
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, CreateView
from django.views.generic.edit import ModelFormMixin, UpdateView

from gcampus.core.decorators import (
    require_permission_edit_measurement,
    require_permission_create_measurement,
)
from gcampus.core.forms.measurement import MeasurementForm
from gcampus.core.forms.water import WaterForm
from gcampus.core.models import Measurement
from gcampus.core.tabs import TabNavigation
from gcampus.core.views.base import TitleMixin, TabsMixin
from gcampus.core.views.forms.tabs import (
    MEASUREMENT_FORM_TABS,
    MeasurementEditTabsMixin,
)


class MeasurementFormViewMixin(ModelFormMixin):
    template_name = "gcampuscore/forms/measurement.html"
    next_view_name = "gcampuscore:edit-chemical-parameters"

    def get_context_data(self, **kwargs):
        if "water_form" not in kwargs:
            kwargs["water_form"] = WaterForm()
        if "loading_texts" not in kwargs:
            req_timeout = getattr(settings, "OVERPASS_TIMEOUT", 20)
            kwargs["loading_texts"] = [
                gettext("Looking for nearby waters on OpenStreetMap."),
                gettext("This may take up to {delay:d} seconds.").format(
                    delay=req_timeout
                ),
                gettext(
                    "It looks like your requests takes a bit longer. "
                    "We are still looking for nearby waters."
                ),
                gettext(
                    "Due to the complexity of geospatial data, "
                    "this may take up to {delay:d} seconds."
                ).format(delay=req_timeout),
            ]
        return super(MeasurementFormViewMixin, self).get_context_data(**kwargs)

    def get_success_url(self):
        return reverse(self.next_view_name, kwargs={"pk": self.object.pk})


class MeasurementCreateView(
    MeasurementFormViewMixin,
    TitleMixin,
    TabsMixin,
    CreateView,
):
    form_class = MeasurementForm
    title = gettext_lazy("Create new measurement")
    tabs = MEASUREMENT_FORM_TABS
    current_tab_name = "meta"

    def get_tabs(self) -> TabNavigation:
        tabs = super(MeasurementCreateView, self).get_tabs()
        # No measurement created yet, disable all other tabs
        tabs["meta"].url = reverse("gcampuscore:add-measurement")
        tabs["chemical"].disabled = True
        tabs["biological"].disabled = True
        tabs["structure"].disabled = True
        return tabs

    @method_decorator(require_permission_create_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form: MeasurementForm):
        instance: Measurement = form.instance
        instance.token = self.request.token
        # Calling ``super`` will call ``form.save`` which in turn calls
        # ``instance.save``.
        return super(MeasurementCreateView, self).form_valid(form)


class MeasurementEditView(
    MeasurementEditTabsMixin, MeasurementFormViewMixin, UpdateView
):
    model = Measurement
    form_class = MeasurementForm
    template_name = MeasurementCreateView.template_name
    next_view_name = MeasurementCreateView.next_view_name
    current_tab_name = "meta"

    @method_decorator(require_permission_edit_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.setdefault("measurement", self._get_measurement())
        return super(MeasurementEditView, self).get_context_data()


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
