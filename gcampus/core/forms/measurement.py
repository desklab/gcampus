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
from gcampus.auth.fields.token import HiddenTokenField, HIDDEN_TOKEN_FIELD_NAME
from gcampus.auth.models.token import (
    can_token_edit_measurement,
    get_token_and_create_permission,
)
from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.models import Measurement, Parameter
from gcampus.map.widgets import GeoPointWidget


class MeasurementForm(ModelForm):
    gcampus_auth_token = HiddenTokenField()

    class Meta:
        model = Measurement
        fields = ("name", "time", "location", "comment", "water")
        field_classes = {"time": SplitSplitDateTimeField}
        widgets = {
            # Inputs with type="datetime-local" are not well-supported
            # to this date. If we decide to replace the
            # SplitSplitDateTimeField later on, we can use the following
            # widget:
            # "time": DateTimeInput(attrs=dict(type="datetime-local")),
            "location": GeoPointWidget(),
        }

    def non_field_errors(self):
        errors = super(MeasurementForm, self).non_field_errors()
        token_errors = self.errors.get(
            HIDDEN_TOKEN_FIELD_NAME, self.error_class(error_class="nonfield")
        )
        return errors + token_errors

    def _clean_fields(self):
        """Clean Fields

        This is where all fields are cleaned. Notice that when running
        :meth:`django.forms.fields.Field.clean`, validators will be run.
        Thus, this is the perfect place to validate and clean the data.
        """
        super(MeasurementForm, self)._clean_fields()

        # Validate token field
        if HIDDEN_TOKEN_FIELD_NAME in self._errors:
            # No need to further validate the token. It is already
            # marked as invalid
            pass
        else:
            current_token = self.cleaned_data[HIDDEN_TOKEN_FIELD_NAME]
            current_instance: Optional[Measurement] = self.instance
            token_error: Optional[ValidationError] = None
            if current_instance is None or current_instance.id in EMPTY_VALUES:
                # Measurement is being created, i.e. the form is used to
                # create a new measurement
                token_instance, permission = get_token_and_create_permission(
                    current_token
                )
                if not permission:
                    token_error = ValidationError(TOKEN_CREATE_PERMISSION_ERROR)
                else:
                    # Save the current token in the instance
                    self.instance.token = token_instance
            else:
                # Measurement is not new but being edited
                if not can_token_edit_measurement(current_token, current_instance):
                    token_error = ValidationError(TOKEN_EDIT_PERMISSION_ERROR)
            if token_error is not None:
                self.add_error(HIDDEN_TOKEN_FIELD_NAME, token_error)


class ParameterForm(ModelForm):
    """Parameter Form

    Data points (see :class:`gcampus.core.models.DataPoint`) are used
    to add data to a measurement. A data point form is always served
    in the context of a measurement, thus, the measurement itself is
    not exposed in the form.

    In most cases, it is advised to use a form set
    (see :attr:`.DataPointFormSet`).
    """

    class Meta:
        model = Parameter
        fields = ["parameter_type", "value", "comment"]
        widgets = {
            "parameter_type": Select(attrs={"class": "form-select form-select-sm"}),
            "value": NumberInput(
                attrs={
                    "class": "form-control form-control-sm",
                    "placeholder": _("Value"),
                }
            ),
            "comment": Textarea(
                attrs={
                    "class": "form-control form-control-sm",
                    "placeholder": _("Note"),
                    "rows": 2,
                }
            ),
        }


class TokenManagementForm(ManagementForm):
    def __init__(self, *args, **kwargs):
        self.base_fields[HIDDEN_TOKEN_FIELD_NAME] = HiddenTokenField()
        super().__init__(*args, **kwargs)

    def check_permission(self, measurement: Measurement) -> bool:
        token = self.cleaned_data[HIDDEN_TOKEN_FIELD_NAME]
        return can_token_edit_measurement(token, measurement)


class DynamicInlineFormset(BaseInlineFormSet):
    _TEMPLATE: str = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields["DELETE"].widget = HiddenInput()

    @property
    def empty_form(self):
        empty_form = super().empty_form
        empty_form.fields["DELETE"].widget = HiddenInput()
        return empty_form

    @cached_property
    def management_form(self):
        """Return the ManagementForm instance for this FormSet."""
        if self.is_bound:
            form = TokenManagementForm(
                self.data, auto_id=self.auto_id, prefix=self.prefix
            )
            # Trigger clean of management form
            form.full_clean()
        else:
            form = TokenManagementForm(
                auto_id=self.auto_id,
                prefix=self.prefix,
                initial={
                    formsets.TOTAL_FORM_COUNT: self.total_form_count(),
                    formsets.INITIAL_FORM_COUNT: self.initial_form_count(),
                    formsets.MIN_NUM_FORM_COUNT: self.min_num,
                    formsets.MAX_NUM_FORM_COUNT: self.max_num,
                },
            )
        return form

    def full_clean(self):
        super(DynamicInlineFormset, self).full_clean()
        if not self.is_bound:
            return
        management_form = self.management_form
        try:
            if not management_form.is_valid():
                if HIDDEN_TOKEN_FIELD_NAME in management_form.errors:
                    # The error is not due to a tampered management form
                    # but due to a missing or invalid auth token.
                    raise ValidationError(TOKEN_EDIT_PERMISSION_ERROR)
                else:
                    raise ValidationError(
                        _("ManagementForm data is missing or has been tampered with"),
                        code="missing_management_form",
                    )
            if not management_form.check_permission(self.instance):
                raise ValidationError(TOKEN_EDIT_PERMISSION_ERROR)
        except ValidationError as e:
            if isinstance(self._non_form_errors, self.error_class):
                self._non_form_errors += self.error_class(e.error_list)
            else:
                self._non_form_errors = self.error_class(e.error_list)


ParameterFormSet: Type[DynamicInlineFormset] = inlineformset_factory(
    Measurement,
    Parameter,
    form=ParameterForm,
    can_delete=True,
    extra=0,
    formset=DynamicInlineFormset,
)
