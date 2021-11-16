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

from typing import Type, Optional

from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES, MaxValueValidator, MinValueValidator
from django.forms import (
    ModelForm,
    inlineformset_factory,
    BaseInlineFormSet,
    IntegerField,
    CharField,
    formsets, Form,
)
from django.forms.formsets import ManagementForm  # noqa
from django.forms.widgets import Select, Textarea, HiddenInput, NumberInput
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from gcampus.auth.exceptions import (
    TOKEN_CREATE_PERMISSION_ERROR,
    TOKEN_EDIT_PERMISSION_ERROR,
)
from gcampus.auth.fields.token import TokenField
from gcampus.auth.models.token import (
    can_token_edit_measurement,
    get_token_and_create_permission,
    CourseToken,
)
from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.models import Measurement, Parameter
from gcampus.map.widgets import GeoPointWidget

TOKEN_FIELD_NAME = "gcampus_auth_token"

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

from typing import Type, Optional

from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django import forms
from django.forms import (
    ModelForm,
    inlineformset_factory,
    BaseInlineFormSet,
    IntegerField,
    CharField,
    formsets,
)
from django.forms.formsets import ManagementForm  # noqa
from django.forms.widgets import Select, Textarea, HiddenInput, NumberInput
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from gcampus.auth.exceptions import (
    TOKEN_CREATE_PERMISSION_ERROR,
    TOKEN_EDIT_PERMISSION_ERROR,
)
from gcampus.auth.fields.token import TokenField
from gcampus.auth.models.token import (
    can_token_edit_measurement,
    get_token_and_create_permission,
)
from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.models import Measurement, Parameter
from gcampus.map.widgets import GeoPointWidget

class GenerateAccesskeysForm(forms.Form):
    generate_accesskeys = forms.IntegerField(label='Generate Accesskeys', min_value=1, max_value=30)

class CourseOverviewForm(ModelForm):
    gcampus_auth_token = TokenField()

    class Meta:
        model = CourseToken
        fields = ["token_name", "teacher_email"]

    def non_field_errors(self):
        errors = super(CourseOverviewForm, self).non_field_errors()
        token_errors = self.errors.get(
            TOKEN_FIELD_NAME, self.error_class(error_class="nonfield")
        )
        return errors + token_errors

    def _clean_fields(self):
        """Clean Fields

        This is where all fields are cleaned. Notice that when running
        :meth:`django.forms.fields.Field.clean`, validators will be run.
        Thus, this is the perfect place to validate and clean the data.
        """
        super(CourseOverviewForm, self)._clean_fields()

        # Validate token field
        if TOKEN_FIELD_NAME in self._errors:
            # No need to further validate the token. It is already
            # marked as invalid
            pass
        else:
            current_token = self.cleaned_data[TOKEN_FIELD_NAME]
            current_instance: Optional[Measurement] = self.instance
            token_error: Optional[ValidationError] = None
            if current_instance is None or current_instance.id in EMPTY_VALUES:
                token_instance, permission = get_token_and_create_permission(
                    current_token
                )
                if not permission:
                    token_error = ValidationError(TOKEN_CREATE_PERMISSION_ERROR)
                else:
                    # Save the current token in the instance
                    self.instance.token = token_instance
