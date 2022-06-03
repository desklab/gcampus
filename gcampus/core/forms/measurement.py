#  Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
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

from typing import Type

from django.forms import (
    ModelForm,
    inlineformset_factory,
    BaseInlineFormSet,
    Form,
    CharField,
    EmailField,
    ChoiceField,
)
from django.forms.widgets import Select, Textarea, HiddenInput, NumberInput
from django.utils.translation import gettext_lazy as _

from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.models import Measurement, Parameter
from gcampus.map.widgets import GeoPointWidget

REPORT_PROBLEM_CHOICES = [
    ("Other", _("Other")),
    ("Note contains problematic text", _("Note contains problematic text")),
    ("Values are problematic", _("Values are problematic")),
    (
        "Location of measurement is not on public ground",
        _("Location of measurement is not on public ground"),
    ),
    (
        "Location of measurement is not on a water",
        _("Location of measurement is not on a water"),
    ),
    (
        "Name of water does not match location",
        _("Name of water does not match location"),
    ),
]


class ReportForm(Form):
    text = CharField(
        required=False,
        label=_("Additional information"),
        widget=Textarea,
        max_length=500,
    )
    problem_choices = ChoiceField(
        label=_("What is the type of the problem?"),
        choices=REPORT_PROBLEM_CHOICES,
    )
    # TODO: Add GDPR link in help text
    email = EmailField(
        required=False,
        label=_("Email address"),
        help_text=_(
            "This email address will only be used to contact you and is not shared "
            "with anyone else."
        ),
    )

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.name == "problem_choices":
                visible.field.widget.attrs["class"] = "form-select"
            else:
                visible.field.widget.attrs["class"] = "form-control"


class MeasurementForm(ModelForm):
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
            "water": HiddenInput(),
        }


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
        fields = ("parameter_type", "value", "comment")
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


ParameterFormSet: Type[DynamicInlineFormset] = inlineformset_factory(
    Measurement,
    Parameter,
    form=ParameterForm,
    can_delete=True,
    extra=0,
    formset=DynamicInlineFormset,
)
