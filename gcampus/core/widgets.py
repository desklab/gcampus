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

import datetime
from typing import Optional

from django.forms import (
    MultiWidget,
    NumberInput,
    DateTimeInput,
    Media,
    TextInput,
    RadioSelect,
    CheckboxInput,
)
from django.forms.utils import to_current_timezone
from django.utils.translation import gettext as _
from django.utils.translation import pgettext
from django_filters.fields import RangeField
from django_filters.widgets import RangeWidget
from leaflet.forms.widgets import LeafletWidget

from gcampus.core.models import Measurement
from gcampus.core.util import (
    get_weeks_from_today,
    convert_dates_to_js_milliseconds,
    get_measurements_per_week,
)


class SplitTimeWidget(MultiWidget):
    supports_microseconds = False
    template_name = "gcampuscore/forms/widgets/splittime.html"

    def __init__(self, attrs=None, time_format=None):
        if attrs is None:
            attrs = {}
        hour_attrs = {
            "title": _("Hour"),
            "maxlength": 2,
            "min": 0,
            "max": 24,
            "placeholder": pgettext("hour input short", "HH"),
        }
        minute_attrs = {
            "title": _("Minute"),
            "maxlength": 2,
            "min": 0,
            "max": 59,
            "placeholder": pgettext("minute input short", "MM"),
        }
        hour_attrs.update(attrs)
        minute_attrs.update(attrs)
        widgets = (NumberInput(attrs=hour_attrs), NumberInput(attrs=minute_attrs))
        self.time_format = time_format
        super().__init__(widgets)

    def decompress(self, value: datetime.time):
        if value:
            return [f"{value.hour:02d}", f"{value.minute:02d}"]
        return [None, None]


class SplitDateWidget(MultiWidget):
    supports_microseconds = False
    template_name = "gcampuscore/forms/widgets/splitdate.html"

    def __init__(self, attrs: Optional[dict] = None, date_format=None):
        if attrs is None:
            attrs = {}
        day_attrs = {
            "title": _("Day"),
            "maxlength": 2,
            "min": 1,
            "max": 31,
            "placeholder": pgettext("day input short", "DD"),
        }
        month_attrs = {
            "title": _("Month"),
            "maxlength": 2,
            "min": 1,
            "max": 12,
            "placeholder": pgettext("month input short", "MM"),
        }
        year_attrs = {
            "maxlength": 4,
            "title": _("Year"),
            "placeholder": pgettext("year input short", "YYYY"),
        }
        day_attrs.update(attrs)
        month_attrs.update(attrs)
        year_attrs.update(attrs)
        widgets = (
            NumberInput(attrs=day_attrs),
            NumberInput(attrs=month_attrs),
            NumberInput(attrs=year_attrs),
        )
        self.date_format = date_format
        super().__init__(widgets)

    def decompress(self, value: datetime.date):
        if value:
            return [f"{value.day:02d}", f"{value.month:02d}", f"{value.year:02d}"]
        return [None, None, None]


class SplitSplitDateTimeWidget(MultiWidget):
    """
    A widget that splits datetime input into two <input type="text"> boxes.
    """

    supports_microseconds = False
    template_name = "gcampuscore/forms/widgets/splitsplitdatetime.html"

    def __init__(
        self,
        attrs=None,
        date_format=None,
        time_format=None,
        date_attrs=None,
        time_attrs=None,
    ):
        widgets = (
            SplitDateWidget(
                attrs=attrs if date_attrs is None else date_attrs,
                date_format=date_format,
            ),
            SplitTimeWidget(
                attrs=attrs if time_attrs is None else time_attrs,
                time_format=time_format,
            ),
        )
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time()]
        return [None, None]


class TimeRangeSlider(RangeWidget):
    template_name = "gcampuscore/forms/widgets/time_range_slider.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        try:
            earliest_date: datetime = Measurement.objects.values_list(
                "time", flat=True
            ).earliest("time")
            week_list = get_weeks_from_today(earliest_date)

            all_dates = list(Measurement.objects.values_list("time", flat=True).all())

            measurements_per_week = get_measurements_per_week(week_list, all_dates)
        except Measurement.DoesNotExist:
            # Create an empty list instead
            week_list = []
            measurements_per_week = []
        context["week_list_js"] = convert_dates_to_js_milliseconds(week_list)
        context["measurements_per_week"] = measurements_per_week
        context["max_measurements_per_week"] = max(measurements_per_week)
        return context


class RangeInput(NumberInput):
    input_type = "range"
    template_name = "gcampuscore/forms/widgets/range_slider.html"


class ToggleInput(CheckboxInput):
    def get_context(self, name, value, attrs):
        attrs = attrs or {}
        klass = "form-check-input"
        if "class" in attrs:
            klass = f"{klass} {attrs['class']}"
        attrs.update({"class": klass, "role": "switch"})
        return super(ToggleInput, self).get_context(name, value, attrs)


class LocationRadiusWidget(MultiWidget):
    map_srid = 4326
    geom_type = "POINT"

    def __init__(self, *args, **kwargs):
        self.map_srid = kwargs.get("map_srid", self.map_srid)
        self.map_widget = LeafletWidget(
            attrs={"map_srid": self.map_srid, "geom_type": self.geom_type}
        )
        self.map_widget.geom_type = self.geom_type
        self.slider_widget = RangeInput(
            attrs={
                "class": "form-range",
                "type": "range",
                "step": "1",
                "min": "1",
                "max": "150",
                "oninput": "viewValue()",
                "id": "slider",
            }
        )
        widgets = (self.map_widget, self.slider_widget)
        super().__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        return value

    def _get_leaflet_map_attrs(self, name, attrs=None):
        """Get Leaflet Map Attributes

        Replicates the functionality of the method
        :meth:`leaflet.forms.widgets.LeafletWidget.get_attr` which
        provides additional context variables used to render a leaflet
        map.

        :param name: Widget name
        :param attrs: Additional attributes
        :return: Dictionary of additional attributes
        :rtype: dict
        """
        return self.map_widget.get_attrs(name, attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        map_widget_name = context["widget"]["subwidgets"][0]["name"]
        context.update(self._get_leaflet_map_attrs(map_widget_name, attrs))
        map_value = value[0]
        if map_value and isinstance(map_value, str):
            map_value = self.map_widget.deserialize(map_value)
        context.update(
            {
                "map_srid": self.map_srid,
                "geom_type": self.geom_type,
                "name": map_widget_name,
                "serialized": self.map_widget.serialize(map_value),
            }
        )
        return context
