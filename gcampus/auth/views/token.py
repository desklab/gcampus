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
    "AccessKeyFormView",
    "CourseTokenFormView",
    "logout",
]

from abc import ABC
from typing import Union, Optional
from urllib.parse import unquote

from django.contrib import messages
from django.contrib.auth import logout as django_logout
from django.contrib.auth import user_logged_out
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy, gettext
from django.views.generic.edit import FormView

from gcampus.auth import session
from gcampus.auth.decorators import throttle
from gcampus.auth.exceptions import TOKEN_INVALID_ERROR
from gcampus.auth.forms.token import (
    AccessKeyForm,
    CourseTokenForm,
    TOKEN_FIELD_NAME,
    NEXT_URL_FIELD_NAME,
)
from gcampus.auth.models.token import CourseToken, TokenType, AccessKey
from gcampus.core.models.util import EMPTY
from gcampus.core.views.base import TitleMixin


class LoginFormView(FormView, TitleMixin, ABC):
    template_name = "gcampusauth/login_form.html"
    success_url = reverse_lazy("gcampuscore:mapview")
    title = gettext_lazy("Login")
    description = gettext_lazy(
        "Login as a student using you access key"
        "to create new measurements and edit your "
        "existing ones. "
        "Teachers can login using a course token "
        "to administer the course, edit measurements and "
        "create new access keys."
    )
    # Has to be set by child classes
    token_type: Optional[TokenType]

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        initial = self.initial.copy()
        if (
            NEXT_URL_FIELD_NAME not in initial
            and self.request.method == "GET"
            and NEXT_URL_FIELD_NAME in self.request.GET
        ):
            initial[NEXT_URL_FIELD_NAME] = unquote(
                self.request.GET.get(NEXT_URL_FIELD_NAME, "")
            )
        return initial

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = self.get_initial()
        if self.token_type is TokenType.access_key:
            context["access_key_form"] = context["form"]
            context["course_token_form"] = CourseTokenForm(initial=initial)
        elif self.token_type is TokenType.course_token:
            context["access_key_form"] = AccessKeyForm(initial=initial)
            context["course_token_form"] = context["form"]
        else:
            context["access_key_form"] = AccessKeyForm(initial=initial)
            context["course_token_form"] = CourseTokenForm(initial=initial)
        return context

    def get_form(self, **kwargs) -> Union[None, AccessKeyForm, CourseTokenForm]:
        if self.token_type is None:
            return None
        return super().get_form(**kwargs)

    def _do_login(self, form: Union[AccessKeyForm, CourseTokenForm]):
        """Login logic for access keys or course tokens.

        The validation for the existence and validity of the provided
        access key or course token is handled by the
        :class:`gcampus.auth.fields.token.HyphenatedTokenField`
        validator.

        :param form: Access key or course token form.
        """
        token = form.cleaned_data[TOKEN_FIELD_NAME]
        if self.token_type is TokenType.course_token:
            token_instance: CourseToken = CourseToken.objects.get(token=token)
        elif self.token_type is TokenType.access_key:
            token_instance: AccessKey = AccessKey.objects.get(token=token)
        else:
            raise RuntimeError()

        session.logout(self.request)
        session.set_token(self.request, token_instance, self.token_type)

    def form_valid(self, form: Union[AccessKeyForm, CourseTokenForm]):
        if form.is_valid():
            self._do_login(form)
            # Check whether an url is provided to which the user should
            # be redirected next. By altering the ``success_url``, the
            # call to ``super`` will automatically redirect to the
            # correct url.
            next_url = form.cleaned_data[NEXT_URL_FIELD_NAME]
            if next_url not in EMPTY:
                self.success_url = unquote(next_url)
            return super(LoginFormView, self).form_valid(form)
        else:
            raise PermissionDenied(TOKEN_INVALID_ERROR)

    @method_decorator(throttle(scope="login_burst"))
    @method_decorator(throttle(scope="login_sustained"))
    def post(self, request, *args, **kwargs):
        return super(LoginFormView, self).post(request, *args, **kwargs)


@receiver(user_logged_out)
def logout_signal(sender, *, request: Optional[HttpRequest] = None, **kwargs):  # noqa
    messages.success(request, gettext("Successfully logged out"))


def logout(request: HttpRequest):
    # Use default django logout
    # This method will flush the current session
    django_logout(request)
    session.logout(request)
    return redirect("gcampuscore:mapview")


class LoginView(LoginFormView):
    token_type = None
    http_method_names = ["get"]


class AccessKeyFormView(LoginFormView):
    form_class = AccessKeyForm
    success_url = reverse_lazy("gcampuscore:mapview")
    token_type = TokenType.access_key


class CourseTokenFormView(LoginFormView):
    form_class = CourseTokenForm
    success_url = reverse_lazy("gcampusauth:course-update")
    token_type = TokenType.course_token
