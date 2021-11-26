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

__all__ = [
    "AccessKeyLoginFormView",
    "CourseTokenLoginFormView",
    "logout",
]

from abc import ABC
from typing import Union, Optional
from urllib.parse import unquote

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout as django_logout, user_logged_out
from django.utils.translation import gettext_lazy, gettext
from django.views.generic.edit import FormView

from gcampus.auth import utils
from gcampus.auth.exceptions import TOKEN_INVALID_ERROR
from gcampus.auth.forms.token import AccessKeyForm, CourseTokenForm, TOKEN_FIELD_NAME, \
    NEXT_URL_FIELD_NAME
from gcampus.auth.models.token import ACCESS_TOKEN_TYPE, COURSE_TOKEN_TYPE, CourseToken
from gcampus.core.models.util import EMPTY
from gcampus.core.views.base import TitleMixin


class LoginFormView(TitleMixin, FormView, ABC):
    template_name = "gcampusauth/forms/token.html"
    title = gettext_lazy("Login")
    token_type: Optional[str] = None
    success_url = reverse_lazy("gcampuscore:mapview")

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
        # Set the current token type
        current_token_type = utils.get_token_type(self.request)
        if current_token_type is not None:
            context["set_token_type"] = current_token_type
        context["token_type"] = self.token_type
        return context

    def form_valid(self, form: Union[AccessKeyForm, CourseTokenForm]):
        if form.is_valid():
            token = form.cleaned_data[TOKEN_FIELD_NAME]
            if self.token_type == COURSE_TOKEN_TYPE:
                token_name = CourseToken.objects.get(token=token).token_name
            else:
                token_name = None
            utils.logout(self.request)
            utils.set_token(self.request, token, self.token_type, token_name)
            next_url = form.cleaned_data[NEXT_URL_FIELD_NAME]
            if next_url not in EMPTY:
                self.success_url = unquote(form.cleaned_data[NEXT_URL_FIELD_NAME])
            return super(LoginFormView, self).form_valid(form)
        raise PermissionDenied(TOKEN_INVALID_ERROR)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=200)


class AccessKeyLoginFormView(LoginFormView):
    title = gettext_lazy("Login as Student")
    form_class = AccessKeyForm
    token_type = ACCESS_TOKEN_TYPE


class CourseTokenLoginFormView(LoginFormView):
    title = gettext_lazy("Login as Teacher")
    form_class = CourseTokenForm
    token_type = COURSE_TOKEN_TYPE


@receiver(user_logged_out)
def logout_signal(sender, *, request: Optional[HttpRequest] = None, **kwargs):
    messages.success(request, gettext("Successfully logged out"))


def logout(request: HttpRequest):
    # Use default django logout
    # This method will flush the current session
    django_logout(request)
    return redirect("gcampuscore:mapview")
