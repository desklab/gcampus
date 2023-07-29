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

import datetime
import logging
from inspect import cleandoc

from django.contrib import messages
from django.core.mail import mail_managers
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext, gettext_lazy
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin

from gcampus.auth.decorators import throttle
from gcampus.auth.models import BaseToken
from gcampus.auth.session import is_authenticated
from gcampus.core.forms.measurement import ReportForm
from gcampus.core.models import Measurement
from gcampus.core.views.base import TitleMixin
from gcampus.core.views.forms import MeasurementDeleteView

logger = logging.getLogger("gcampus.core.views.details.measurement")


class MeasurementDetailView(FormMixin, TitleMixin, DetailView):
    model = Measurement
    queryset = Measurement.objects.select_related("water", "token").prefetch_related(
        "parameters"
    )
    template_name = "gcampuscore/sites/detail/measurement_detail.html"
    description = gettext_lazy(
        "Learn more about the measurement, explore nearby and similar "
        "measurements, and download a PDF summary of this measurement "
        "to discuss the results with others."
    )
    form_class = ReportForm
    object: Measurement

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

    @method_decorator(throttle("measurement_report"))
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
        self.object.requires_review = True
        self.object.save(update_fields=("requires_review",))
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
