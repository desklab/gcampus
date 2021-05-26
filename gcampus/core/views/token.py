from django.views.generic.edit import FormView

from gcampus.core.models import StudentToken


class SetStudentToken(FormView):
    form_class = StudentToken
