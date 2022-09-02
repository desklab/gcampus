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

import datetime
import logging
from inspect import cleandoc

from django.contrib import messages
from django.conf import settings
from django.core.mail import mail_managers
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext, gettext_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
    ModelFormMixin,
    FormMixin,
)

from gcampus.auth.decorators import throttle
from gcampus.auth.models.token import BaseToken
from gcampus.auth.session import is_authenticated
from gcampus.core.decorators import (
    require_permission_create_measurement,
    require_permission_edit_measurement,
)
from gcampus.core.forms.measurement import MeasurementForm, ReportForm
from gcampus.core.forms.water import WaterForm
from gcampus.core.models import Measurement
from gcampus.core.views.base import TitleMixin
from gcampus.core.views.measurement.list import MeasurementListView

logger = logging.getLogger("gcampus.core.views.measurement")


class MeasurementDetailView(FormMixin, TitleMixin, DetailView):
    model = Measurement
    queryset = Measurement.objects.select_related("water", "token").prefetch_related(
        "parameters"
    )
    template_name = "gcampuscore/sites/detail/measurement_detail.html"
    form_class = ReportForm

    def get_context_data(self, **kwargs):
        kwargs.setdefault("can_edit", False)
        if is_authenticated(self.request) and self.object:
            token: BaseToken = self.request.token
            if token.has_perm("gcampuscore.change_measurement", obj=self.object):
                # Measurement can be edited by the current token user
                # Create an empty form from the MeasurementDeleteView
                # to display a delete button.
                kwargs["can_edit"] = True
                kwargs["delete_form"] = MeasurementDeleteView.form_class()
        return super(MeasurementDetailView, self).get_context_data(**kwargs)

    def get_title(self) -> str:
        if self.object:
            return str(self.object)
        else:
            raise RuntimeError("'self.object' is not set")

    @method_decorator(throttle())
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    @classmethod
    def create_measurement_report_string(cls, form, current_url: str, admin_url: str):
        """Create Measurement Report String

        This function takes the form and extracts problem type and the
        string that were submitted by a user at the measurement detail
        page and converts them into a string that is sent via email to
        the managers

        :param form: List of checked problem types
        :param current_url: URL of the user
        :param admin_url: URL to measurement in admin interface
        :returns: Email string
        """

        now = datetime.datetime.now()
        problem_type = form["problem_choices"].data

        email_string = f"""
        A user has submitted a problem with the following measurement:
        
        '{admin_url}'
        
        From url: {current_url}
        
        Time: {now}
        
        Problem type: {problem_type}

        Additional information: {form.cleaned_data['text'] or '-'}
        
        E-Mail address: {form.cleaned_data['email'] or '-'}
        """
        return cleandoc(email_string)

    def form_valid(self, form):
        current_url = self.request.get_full_path()
        info = self.model._meta.app_label, self.model._meta.model_name  # noqa
        admin_url = reverse(
            "admin:%s_%s_change" % info, kwargs=dict(object_id=self.object.pk)
        )
        logger.debug(
            f"Measurement reported, current URL: {current_url}, admin URL: {admin_url}"
        )
        messages.success(
            self.request,
            message=gettext(
                "You have successfully reported this measurement. The team has been "
                "informed and will look into your request as soon as possible."
            ),
        )
        email_text = self.create_measurement_report_string(form, current_url, admin_url)
        mail_managers(f"Measurement reported: {self.object!s}", email_text)
        return super(MeasurementDetailView, self).form_valid(form)

    def get_success_url(self):
        return reverse("gcampuscore:measurement-detail", kwargs={"pk": self.object.id})


class MeasurementMapView(TitleMixin, ListView):
    model = Measurement
    title = "GewässerCampus"
    template_name = "gcampuscore/sites/mapview.html"


class MeasurementFormViewMixin(TitleMixin, ModelFormMixin):
    template_name = "gcampuscore/forms/measurement.html"
    next_view_name = "gcampuscore:add-chemical-parameters"

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


class MeasurementCreateView(MeasurementFormViewMixin, CreateView):
    form_class = MeasurementForm
    title = gettext_lazy("Create new measurement")

    @method_decorator(require_permission_create_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form: MeasurementForm):
        instance: Measurement = form.instance
        instance.token = self.request.token
        # Calling ``super`` will call ``form.save`` which in turn calls
        # ``instance.save``.
        return super(MeasurementCreateView, self).form_valid(form)


class MeasurementEditView(MeasurementFormViewMixin, UpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = MeasurementCreateView.template_name
    next_view_name = MeasurementCreateView.next_view_name

    @method_decorator(require_permission_edit_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_title(self) -> str:
        return gettext("Edit Measurement {pk:d} - Information").format(
            pk=self.object.pk
        )


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
