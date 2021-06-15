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
from django.forms.widgets import Select, TextInput, Textarea, HiddenInput
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from leaflet.forms.widgets import LeafletWidget

from gcampus.auth.fields.token import TokenField
from gcampus.auth.models.token import (
    can_token_edit_measurement,
    get_token_and_create_permission,
)
from gcampus.auth.exceptions import (
    TOKEN_CREATE_PERMISSION_ERROR,
    TOKEN_EDIT_PERMISSION_ERROR,
)
from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.models import Measurement, DataPoint

TOKEN_FIELD_NAME = "gcampus_auth_token"


class MeasurementForm(ModelForm):
    gcampus_auth_token = TokenField()

    class Meta:
        model = Measurement
        fields = ["name", "time", "location", "comment", "water_name", "osm_id"]
        field_classes = {"time": SplitSplitDateTimeField}
        widgets = {
            "location": LeafletWidget(),
        }

    def non_field_errors(self):
        errors = super(MeasurementForm, self).non_field_errors()
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
        super(MeasurementForm, self)._clean_fields()

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
                token_instance, permission = (
                    get_token_and_create_permission(current_token)
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
                self.add_error(TOKEN_FIELD_NAME, token_error)

        water_name = self.cleaned_data["water_name"]
        if "gcampus_osm_id" in water_name:
            # The water_name includes a OpenStreetMap ID and will
            # thus be parsed to save this ID in a separate column.
            osm_id_field: IntegerField = self.fields["osm_id"]
            water_name_field: CharField = self.fields["water_name"]
            try:
                name, osm_id = water_name.split(" gcampus_osm_id:")
                # Make sure the fields are cleaned because the field may
                # contain malicious user input. A gcampus_osm_id can be
                # passed by any used when using the variable water name
                # field.
                name = water_name_field.clean(name)
                osm_id = osm_id_field.clean(osm_id)
                self.cleaned_data["water_name"] = name
                self.cleaned_data["osm_id"] = osm_id
            except (ValueError, OverflowError, TypeError, ValidationError):
                error = ValidationError(_("Unable to parse OpenStreetMap ID!"))
                self.add_error("water_name", error)


class DataPointForm(ModelForm):
    """Data Point Form

    Data points (see :class:`gcampus.core.models.DataPoint`) are used
    to add data to a measurement. A data point form is always served
    in the context of a measurement, thus, the measurement itself is
    not exposed in the form.

    In most cases, it is advised to use a form set
    (see :attr:`.DataPointFormSet`).
    """

    class Meta:
        model = DataPoint
        fields = ["data_type", "value", "comment"]
        widgets = {
            "data_type": Select(attrs={"class": "form-select form-select-sm"}),
            "value": TextInput(
                attrs={
                    "class": "form-control form-control-sm",
                    "placeholder": _("Value"),
                }
            ),
            "comment": Textarea(
                attrs={
                    "class": "form-control form-control-sm",
                    "placeholder": _("Comment"),
                    "rows": 2,
                }
            ),
        }


class TokenManagementForm(ManagementForm):
    def __init__(self, *args, **kwargs):
        self.base_fields[TOKEN_FIELD_NAME] = TokenField()
        super().__init__(*args, **kwargs)

    def check_permission(self, measurement: Measurement) -> bool:
        token = self.cleaned_data[TOKEN_FIELD_NAME]
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
                if TOKEN_FIELD_NAME in management_form.errors:
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


DataPointFormSet: Type[DynamicInlineFormset] = inlineformset_factory(
    Measurement,
    DataPoint,
    form=DataPointForm,
    can_delete=True,
    extra=0,
    formset=DynamicInlineFormset,
)
