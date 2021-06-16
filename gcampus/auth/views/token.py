from abc import ABC
from typing import Union, Optional

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from gcampus.auth import utils
from gcampus.auth.exceptions import TOKEN_INVALID_ERROR
from gcampus.auth.forms.token import AccessKeyForm, CourseTokenForm
from gcampus.auth.models.token import ACCESS_TOKEN_TYPE, COURSE_TOKEN_TYPE


class SetTokenFormView(FormView, ABC):
    template_name = "gcampusauth/forms/token.html"
    success_url = reverse_lazy("gcampuscore:mapview")
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
            utils.logout(self.request)
            utils.set_token(self.request, token, self.token_type)
            return super(SetTokenFormView, self).form_valid(form)
        raise PermissionDenied(TOKEN_INVALID_ERROR)


class SetAccessKeyFormView(SetTokenFormView):
    form_class = AccessKeyForm
    token_type = ACCESS_TOKEN_TYPE


class SetCourseTokenFormView(SetTokenFormView):
    form_class = CourseTokenForm
    token_type = COURSE_TOKEN_TYPE


def logout(request: HttpRequest):
    utils.logout(request)
    return render(request, "gcampusauth/forms/logout.html")
