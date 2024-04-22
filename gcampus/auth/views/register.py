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

__all__ = [
    "RegisterFormView",
]

import logging
import re
import time

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.views.generic import CreateView

from gcampus.auth.decorators import throttle
from gcampus.auth.forms import RegisterForm
from gcampus.auth.models import Course
from gcampus.core.views.base import TitleMixin

_REGISTER_TIMESTAMP_SESSION_KEY = "gcampusauth_register_timestamp"

# Regex to detect spam (random) school, teacher or course names.
# Matches single words with two or more changes from lower to upper or
# from upper to lower caps.
_SPAM_REGEX = re.compile(r"([a-z]|[A-Z])([a-z]+[A-Z]+|[A-Z]+[a-z]+){2,}[a-zA-Z]*")

logger = logging.getLogger("gcampus.auth.views.register")


class RegisterFormView(TitleMixin, CreateView):
    form_class = RegisterForm
    model = Course
    template_name_suffix = "_create_form"
    title = gettext_lazy("Register a new course")
    description = gettext_lazy(
        "Register your class or course and generate a list"
        "of access keys for your students. "
        "These keys can be used to create and later edit "
        "measurements on GewässerCampus. "
        "Alongside the generated access keys, you will also "
        "receive a course token that should be kept "
        "private. With this key you can view and edit all "
        "your student's measurements."
    )
    success_url = reverse_lazy("gcampuscore:mapview")
    object: Course

    def get(self, request, *args, **kwargs):
        """Get request.

        Save the current time as a timestamp in the users' session. This
        is later used to measure the time it took to fill out the form.
        """
        request.session[_REGISTER_TIMESTAMP_SESSION_KEY] = time.time()
        return super(RegisterFormView, self).get(request, *args, **kwargs)

    @method_decorator(throttle(scope="registration_burst"))
    @method_decorator(throttle(scope="registration_sustained"))
    def post(self, request, *args, **kwargs):
        return super(RegisterFormView, self).post(request, *args, **kwargs)

    def is_spam(self, form: RegisterForm) -> bool:
        """Check if the form submission looks like typical spam
        submissions.

        There are two checks in place: Pattern-matching of all three
        form fields and a time-based check.
        If all three form fields match the pattern, they are considered
        spam. If not but the user filled out the form in less then the
        specified time, the form is equally considered spam.
        """
        logger.info("Check 'register' submission for spam...")
        time_now = time.time()  # already retrieve the current time.
        school_name = form.cleaned_data["school_name"]
        teacher_name = form.cleaned_data["teacher_name"]
        name = form.cleaned_data["name"]
        if school_name and teacher_name and name:
            if (
                _SPAM_REGEX.fullmatch(school_name)
                and _SPAM_REGEX.fullmatch(teacher_name)
                and _SPAM_REGEX.fullmatch(name)
            ):
                logger.warning("Submission considered spam: Spam regex matched")
                return True

        timestamp: float | None = self.request.session.get(
            _REGISTER_TIMESTAMP_SESSION_KEY, None
        )
        if timestamp is None:
            # Session has no timestamp information, e.g. because of
            # automated spam.
            logger.warning(
                "Submission considered spam: No timestamp information in session"
            )
            return True
        else:
            min_delay = getattr(settings, "REGISTER_MIN_FORM_DELAY", 12)
            if timestamp is not None and (time_now - timestamp) < min_delay:
                logger.warning("Submission considered spam: Submission too fast")
                return True
        logger.info("Submission passed spam checks")
        return False

    def form_valid(self, form):
        """Form is considered valid. Check for spam and save if not
        spam. Sends a message to the user."""
        # This 'Accept' header is rather uncommon, but all spam
        # submissions come with that 'Accept' header. We minimize the
        # false-positive (legitimate submissions classified as spam)
        # by filtering out only these requests.
        if self.request.headers.get("Accept", "*/*") == "*/*":
            # Check if the submission is considered spam.
            if self.is_spam(form):
                # Add a generic error. Note that the timestamp is NOT reset,
                # such that the user can resubmit the form and potentially
                # pass the time-based check.
                # This is by design, we assume that spam submissions will
                # disregard the
                form.add_error(
                    None,
                    ValidationError(
                        _("Something went wrong, please try again or contact us.")
                    ),
                )
                return self.form_invalid(form)
        super(RegisterFormView, self).form_valid(form)
        messages.success(
            self.request,
            _(
                "You successfully registered a course. "
                "An activation link has been sent to your email address."
            ),
        )
        # In older versions of this function, the user has been logged
        # in automatically. This has been changed to the following:
        #  - Tokens of a new course can not sign in as they are marked
        #    'not active' as long as their email is not verified.
        #  - Once an email has been verified, the user is automatically
        #    logged in with the course token associated with that
        #    course.
        return HttpResponseRedirect(self.get_success_url())
