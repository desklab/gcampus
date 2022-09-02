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

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import (
    ModelForm,
    inlineformset_factory,
    BaseInlineFormSet,
    Form,
    CharField,
    EmailField,
    ChoiceField,
    ModelChoiceField,
)
from django.forms.widgets import Select, Textarea, HiddenInput, NumberInput
from django.utils.formats import localize
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.models import Measurement, Parameter, ParameterType
from gcampus.core.models.measurement import ParameterTypeCategory
from gcampus.map.widgets import GeoPointWidget

_MIN_TIME = settings.MEASUREMENT_MIN_TIME
_MAX_TIME = settings.MEASUREMENT_MAX_TIME
_MIN_TIME_ERROR = _("The measurement time has to be after {time!s}.").format(
    time=localize(localtime(_MIN_TIME))
)
_MAX_TIME_ERROR = _("The measurement time has to be before {time!s}.").format(
    time=localize(localtime(_MAX_TIME))
)
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
    email = EmailField(
        required=False,
        label=_("Email address"),
        help_text=_(
            "This email address will only be used to contact you and is not shared "
            "with anyone else. See our privacy policy for more details."
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
    time = SplitSplitDateTimeField(
        label=pgettext_lazy("measurement time", "Time"),
        help_text=_("Date and time of the measurement"),
        validators=(
            MinValueValidator(_MIN_TIME, message=_MIN_TIME_ERROR),
            MaxValueValidator(_MAX_TIME, message=_MAX_TIME_ERROR),
        ),
    )

    class Meta:
        model = Measurement
        fields = ("name", "location", "comment", "water", "time")
        widgets = {
            # Inputs with type="datetime-local" are not well-supported
            # to this date. If we decide to replace the
            # SplitSplitDateTimeField later on, we can use the following
            # widget:
            # "time": DateTimeInput(attrs=dict(type="datetime-local")),
            "location": GeoPointWidget(),
            "water": HiddenInput(),
        }
        error_messages = {
            "location": {
                "required": _(
                    "No location has been selected. "
                    "Click on the map to select the location of your measurement."
                ),
            },
            "water": {
                "required": _(
                    "No water has been selected. "
                    "After selecting a location on the map, choose one of the "
                    "suggested nearby waters."
                ),
            },
        }


class ChemicalParameterForm(ModelForm):
    """Parameter Form

    Data points (see :class:`gcampus.core.models.DataPoint`) are used
    to add data to a measurement. A data point form is always served
    in the context of a measurement, thus, the measurement itself is
    not exposed in the form.

    In most cases, it is advised to use a form set
    (see :attr:`.DataPointFormSet`).
    """

    parameter_type = ModelChoiceField(queryset=ParameterType.objects.filter(
        category=ParameterTypeCategory.CHEMICAL))

    class Meta:
        model = Parameter
        fields = ("parameter_type", "value", "comment")
        widgets = {
            "parameter_type": Select(
                attrs={"class": "form-select form-select-sm"}),
            "value": NumberInput(
                attrs={
                    "class": "form-control form-control-sm",
                    "placeholder": _("Value"),
                    "min": 0,
                    "max": 100000,
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


class BiologicalParameterForm(ModelForm):
    """Parameter Form

    Data points (see :class:`gcampus.core.models.DataPoint`) are used
    to add data to a measurement. A data point form is always served
    in the context of a measurement, thus, the measurement itself is
    not exposed in the form.

    In most cases, it is advised to use a form set
    (see :attr:`.DataPointFormSet`).
    """

    parameter_type = ModelChoiceField(queryset=ParameterType.objects.filter(
        category=ParameterTypeCategory.BIOLOGICAL))

    class Meta:
        model = Parameter
        fields = ("parameter_type", "value", "comment")
        widgets = {
            "parameter_type": Select(
                attrs={"class": "form-select form-select-sm"}),
            "value": NumberInput(
                attrs={
                    "class": "form-control form-control-sm",
                    "placeholder": _("Value"),
                    "min": 0,
                    "max": 100000,
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


class BaseParameterFormset(DynamicInlineFormset):
    parameter_category: ParameterTypeCategory

    def __init__(self, *args, **kwargs):
        if not hasattr(self, "parameter_category"):
            raise NotImplementedError(
                "'parameter_category' has to be specified!")
        kwargs.setdefault(
            "queryset",
            Parameter.objects.filter(
                parameter_type__category=self.parameter_category)
        )
        super(BaseParameterFormset, self).__init__(*args, **kwargs)


class ChemicalParameterFormset(BaseParameterFormset):
    parameter_category: ParameterTypeCategory = ParameterTypeCategory.CHEMICAL


class BiologicalParameterFormset(BaseParameterFormset):
    parameter_category: ParameterTypeCategory = ParameterTypeCategory.BIOLOGICAL


ChemicalParameterFormSet: Type[DynamicInlineFormset] = inlineformset_factory(
    Measurement,
    Parameter,
    form=ChemicalParameterForm,
    can_delete=True,
    extra=0,
    formset=DynamicInlineFormset,
)

BiologicalParameterFormSet: Type[DynamicInlineFormset] = inlineformset_factory(
    Measurement,
    Parameter,
    form=BiologicalParameterForm,
    can_delete=True,
    extra=0,
    formset=DynamicInlineFormset,
)
