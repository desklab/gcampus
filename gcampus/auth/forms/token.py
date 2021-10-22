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

TOKEN_FIELD_NAME = "token"


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


class RegisterForm(forms.ModelForm):
    number_of_tokens = forms.IntegerField(
        min_value=1,
        max_value=getattr(settings, "REGISTER_MAX_TOKEN_NUMBER", 30),
        required=True,
        initial=5,
    )

    class Meta:
        model = CourseToken
        fields = (
            "school_name",
            "teacher_name",
            "teacher_email",
            "token_name",
        )
