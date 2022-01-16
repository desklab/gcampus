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

from gcampus.auth.fields.token import (
    HiddenTokenField,
    course_token_exists_validator,
    HIDDEN_TOKEN_FIELD_NAME,
)
from gcampus.auth.models.token import (
    CourseToken,
)


class GenerateAccessKeysForm(forms.Form):
    count = forms.IntegerField(
        label="Generate Accesskeys",
        min_value=1,
        max_value=getattr(settings, "REGISTER_MAX_ACCESS_KEY_NUMBER", 30),
    )


class CourseOverviewForm(forms.ModelForm):
    gcampus_auth_token = HiddenTokenField(validators=[course_token_exists_validator])

    class Meta:
        model = CourseToken
        fields = ["token_name", "school_name", "teacher_email"]

    def non_field_errors(self):
        errors = super(CourseOverviewForm, self).non_field_errors()
        token_errors = self.errors.get(
            HIDDEN_TOKEN_FIELD_NAME, self.error_class(error_class="nonfield")
        )
        return errors + token_errors
