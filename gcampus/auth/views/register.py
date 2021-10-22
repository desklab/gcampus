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
from django.http import HttpResponseBadRequest
from django.urls import reverse_lazy, resolve
from django.views.generic import FormView, ListView, DetailView
from django.core.exceptions import SuspiciousOperation, PermissionDenied

from gcampus.auth import exceptions
from gcampus.auth.forms.token import RegisterForm
from gcampus.auth.models import CourseToken, AccessKey


class RegisterFormView(FormView):
    form_class = RegisterForm
    template_name = "gcampusauth/forms/register.html"
    # success_url = reverse_lazy("gcampusauth:register_success")

    def form_valid(self, form):
        if form.is_valid():
            number_of_tokens = form.cleaned_data["number_of_tokens"]
            school_name = form.cleaned_data["school_name"]
            teacher_name = form.cleaned_data["teacher_name"]
            teacher_email = form.cleaned_data["teacher_email"]
            token_name = form.cleaned_data["token_name"]

            course_token = CourseToken(
                school_name=school_name,
                teacher_name=teacher_name,
                teacher_email=teacher_email,
                token_name=token_name,
            )
            course_token.save()
            self.pk = course_token.pk
            for i in range(number_of_tokens):
                access_key = AccessKey.generate_access_key()
                AccessKey(token=access_key, parent_token=course_token).save()
            return super(RegisterFormView, self).form_valid(form)
        # TODO choose better exception
        raise SuspiciousOperation("Something went wrong")

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=200)

    def get_success_url(self):
        token = CourseToken.objects.get(pk=self.pk)
        return reverse_lazy(
            "gcampusauth:register_success", kwargs={"pk": self.pk, "token": token.token}
        )


class RegisterSuccessView(DetailView):
    model = CourseToken
    template_name = "gcampusauth/sites/register_success.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        url_token = self.request.path.split("/")[-1]
        if url_token != kwargs["object"].token:
            raise PermissionDenied(exceptions.TOKEN_INVALID_ERROR)
        context = super().get_context_data(**kwargs)
        course_token = self.object
        context["children_token"] = AccessKey.objects.filter(parent_token=course_token)
        return context
