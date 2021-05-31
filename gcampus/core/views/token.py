from django.views.generic.edit import FormView

from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from gcampus.core.forms.token import StudentTokenForm, TeacherTokenForm
from gcampus.core.models.token import STUDENT_TOKEN_TYPE


class SetStudentTokenFormView(FormView):
    template_name = "gcampuscore/forms/token.html"
    form_class = StudentTokenForm
    # TODO Create an intermediate site that tells you you logged in
    #   correctly and gives the option for several sites
    success_url = "/mapview/"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["token_type"] = "Student"
        return context

    def form_valid(self, form: StudentTokenForm):
        if form.is_valid():
            token = form.cleaned_data["token"]
            self.request.session["token"] = token
            self.request.session["token_type"] = STUDENT_TOKEN_TYPE
            return super(SetStudentTokenFormView, self).form_valid(form)
        raise PermissionDenied(_("Token does not exist"))


class SetTeacherTokenFormView(FormView):
    template_name = "gcampuscore/forms/token.html"
    form_class = TeacherTokenForm
    # TODO Create an intermediate site that tells you you logged in correctly and gives the option for several sites
    success_url = "/mapview/"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["token_type"] = "Teacher"
        return context

    def form_valid(self, form: TeacherTokenForm):
        if form.is_valid():
            token = form.cleaned_data["token"]
            self.request.session["teacherToken"] = token
            return super(SetTeacherTokenFormView, self).form_valid(form)
        raise PermissionDenied(_("Token does not exist"))
