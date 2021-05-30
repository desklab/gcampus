from django.core.exceptions import ValidationError
from django.forms import (
    ModelForm,
    inlineformset_factory,
    BaseInlineFormSet,
    IntegerField,
    CharField,
)
from django.forms.widgets import Select, TextInput, Textarea, HiddenInput
from django.utils.translation import gettext_lazy as _
from leaflet.forms.widgets import LeafletWidget

from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.models import Measurement, DataPoint


class MeasurementForm(ModelForm):
    class Meta:
        model = Measurement
        fields = ["name", "time", "location", "comment", "location_name", "osm_id"]
        field_classes = {"time": SplitSplitDateTimeField}
        widgets = {
            "location": LeafletWidget(),
        }

    def _clean_fields(self):
        super(MeasurementForm, self)._clean_fields()
        location_name = self.cleaned_data["location_name"]
        if "gcampus_osm_id" in location_name:
            # The location_name includes a OpenStreetMap ID and will
            # thus be parsed to save this ID in a separate column.
            osm_id_field: IntegerField = self.fields["osm_id"]
            location_name_field: CharField = self.fields["location_name"]
            try:
                name, osm_id = location_name.split(" gcampus_osm_id:")
                # Make sure the fields are cleaned because the field may
                # contain malicious user input. A gcampus_osm_id can be
                # passed by any used when using the variable water name
                # field.
                name = location_name_field.clean(name)
                osm_id = osm_id_field.clean(osm_id)
                self.cleaned_data["location_name"] = name
                self.cleaned_data["osm_id"] = osm_id
            except (ValueError, OverflowError, TypeError, ValidationError):
                error = ValidationError(_("Unable to parse OpenStreetMap ID!"))
                self.add_error("location_name", error)

    def save(self, token, *args, **kwargs):  # noqa
        # TODO check token call permission function

        super(MeasurementForm, self).save(*args, **kwargs)


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


DataPointFormSet = inlineformset_factory(
    Measurement,
    DataPoint,
    form=DataPointForm,
    can_delete=True,
    extra=0,
    formset=DynamicInlineFormset,
)
