from django.views.generic import FormView

from gcampus.auth.forms.token import RegisterForm


class RegisterFormView(FormView):
    form_class = RegisterForm
    template_name = "gcampusauth/forms/register.html"
