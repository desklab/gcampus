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
    "SetAccessKeyFormView",
    "SetCourseTokenFormView",
    "logout",
    "login_success",
]

from abc import ABC
from typing import Union, Optional

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views.generic.edit import FormView

from gcampus.auth import utils
from gcampus.auth.exceptions import TOKEN_INVALID_ERROR
from gcampus.auth.forms.token import AccessKeyForm, CourseTokenForm
from gcampus.auth.models.token import ACCESS_TOKEN_TYPE, COURSE_TOKEN_TYPE, CourseToken
from gcampus.core.views.base import TitleMixin


class SetTokenFormView(TitleMixin, FormView, ABC):
    template_name = "gcampusauth/forms/token.html"
    title = gettext_lazy("Login")
    success_url = reverse_lazy("gcampusauth:login_success")
    token_type: Optional[str] = None

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
            token = form.cleaned_data["token"]
            if self.token_type == COURSE_TOKEN_TYPE:
                token_name = CourseToken.objects.get(token=token).token_name
            else:
                token_name = None
            utils.logout(self.request)
            utils.set_token(self.request, token, self.token_type, token_name)
            return super(SetTokenFormView, self).form_valid(form)
        raise PermissionDenied(TOKEN_INVALID_ERROR)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=200)


class SetAccessKeyFormView(SetTokenFormView):
    title = gettext_lazy("Login as Student")
    form_class = AccessKeyForm
    token_type = ACCESS_TOKEN_TYPE


class SetCourseTokenFormView(SetTokenFormView):
    title = gettext_lazy("Login as Teacher")
    form_class = CourseTokenForm
    token_type = COURSE_TOKEN_TYPE


def logout(request: HttpRequest):
    utils.logout(request)
    return render(request, "gcampusauth/forms/logout.html")


def login_success(request: HttpRequest):
    return render(request, "gcampusauth/sites/login_success.html")
