from django import forms
from django.utils.translation import gettext_lazy as _

from gcampus.auth.fields.token import (
    student_token_exists_validator,
    teacher_token_exists_validator,
)
from gcampus.auth.models.token import (
    STUDENT_TOKEN_LENGTH,
    TEACHER_TOKEN_LENGTH
)


class StudentTokenForm(forms.Form):
    token = forms.CharField(
        required=True,
        label=_("Student Token"),
        max_length=STUDENT_TOKEN_LENGTH,
        min_length=STUDENT_TOKEN_LENGTH,
        validators=[student_token_exists_validator],
    )
    fields = ["token"]


class TeacherTokenForm(forms.Form):
    token = forms.CharField(
        required=True,
        label=_("Teacher Token"),
        max_length=TEACHER_TOKEN_LENGTH,
        min_length=TEACHER_TOKEN_LENGTH,
        validators=[teacher_token_exists_validator],
    )
    fields = ["token"]
