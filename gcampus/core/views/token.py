from abc import ABC
from typing import Union, Optional

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from gcampus.core.forms.token import StudentTokenForm, TeacherTokenForm
from gcampus.core.models.token import (
    STUDENT_TOKEN_TYPE,
    TEACHER_TOKEN_TYPE,
    TOKEN_INVALID_ERROR,
    TEACHER_TOKEN_LENGTH,
    STUDENT_TOKEN_LENGTH,
)


class SetTokenFormView(FormView, ABC):
    template_name = "gcampuscore/forms/token.html"
    success_url = reverse_lazy("gcampuscore:mapview")
    token_type: Optional[str] = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # Set the current token type
        current_token = self.request.session.get("token", "")
        if len(current_token) == TEACHER_TOKEN_LENGTH:
            context["set_token_type"] = TEACHER_TOKEN_TYPE
        elif len(current_token) == STUDENT_TOKEN_LENGTH:
            context["set_token_type"] = STUDENT_TOKEN_TYPE
        context["token_type"] = self.token_type
        return context

    def form_valid(self, form: Union[StudentTokenForm, TeacherTokenForm]):
        if form.is_valid():
            delete_token(self.request)
            token = form.cleaned_data["token"]
            self.request.session["token"] = token
            self.request.session["token_type"] = self.token_type
            return super(SetTokenFormView, self).form_valid(form)
        raise PermissionDenied(TOKEN_INVALID_ERROR)


class SetStudentTokenFormView(SetTokenFormView):
    form_class = StudentTokenForm
    token_type = STUDENT_TOKEN_TYPE


class SetTeacherTokenFormView(SetTokenFormView):
    form_class = TeacherTokenForm
    token_type = TEACHER_TOKEN_TYPE


def delete_token(request: HttpRequest):
    if request.session.get("token", None) is not None:
        del request.session["token"]


def logout(request: HttpRequest):
    delete_token(request)
    return render(request, "gcampuscore/forms/logout.html")
