from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from gcampus.auth.fields.token import (
    access_key_exists_validator,
    course_token_exists_validator,
)
from gcampus.auth.models.token import (
    ACCESS_KEY_LENGTH,
    COURSE_TOKEN_LENGTH,
    CourseToken,
)


class AccessKeyForm(forms.Form):
    token = forms.CharField(
        required=True,
        label=_("Access Key"),
        max_length=ACCESS_KEY_LENGTH,
        min_length=ACCESS_KEY_LENGTH,
        validators=[access_key_exists_validator],
    )
    fields = ["token"]


class CourseTokenForm(forms.Form):
    token = forms.CharField(
        required=True,
        label=_("Course Token"),
        max_length=COURSE_TOKEN_LENGTH,
        min_length=COURSE_TOKEN_LENGTH,
        validators=[course_token_exists_validator],
    )
    fields = ["token"]
