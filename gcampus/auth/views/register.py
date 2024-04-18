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
        request.session[_REGISTER_TIMESTAMP_SESSION_KEY] = time.time()
        return super(RegisterFormView, self).get(request, *args, **kwargs)

    @method_decorator(throttle(scope="registration_burst"))
    @method_decorator(throttle(scope="registration_sustained"))
    def post(self, request, *args, **kwargs):
        return super(RegisterFormView, self).post(request, *args, **kwargs)

    def is_spam(self, form: RegisterForm) -> bool:
        school_name = form.cleaned_data["school_name"]
        teacher_name = form.cleaned_data["teacher_name"]
        name = form.cleaned_data["name"]
        if school_name and teacher_name and name:
            if (
                _SPAM_REGEX.fullmatch(school_name)
                and _SPAM_REGEX.fullmatch(teacher_name)
                and _SPAM_REGEX.fullmatch(name)
            ):
                return True

        timestamp: float | None = self.request.session.get(
            _REGISTER_TIMESTAMP_SESSION_KEY, None
        )
        if timestamp is not None:
            min_delay = getattr(settings, "REGISTER_MIN_FORM_DELAY", 12)
            return timestamp is not None and (time.time() - timestamp) < min_delay

    def form_valid(self, form):
        if self.is_spam(form):
            form.add_error(
                None,
                ValidationError(
                    _("Something went wrong, please try again later or contact us.")
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
