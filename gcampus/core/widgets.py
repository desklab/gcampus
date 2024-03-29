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

import datetime
from typing import Optional

from django.conf import settings
from django.forms import MultiWidget, NumberInput, CheckboxInput
from django.forms.utils import to_current_timezone
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import pgettext
from django_filters.widgets import RangeWidget

from gcampus.core.models import Measurement
from gcampus.core.util import (
    get_intervals_from_today,
    convert_dates_to_js_milliseconds,
    get_measurement_intervals,
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
        min_time: datetime.datetime = settings.MEASUREMENT_MIN_TIME
        max_time: datetime.datetime = settings.MEASUREMENT_MAX_TIME
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
            "minlength": 4,
            "maxlength": 4,
            "min": min_time.year,
            "max": max_time.year,
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
            interval_list = get_intervals_from_today(earliest_date)

            all_dates = list(
                Measurement.objects.values_list("time", flat=True).filter(hidden=False)
            )

            measurements_per_interval = get_measurement_intervals(
                interval_list, all_dates
            )
        except Measurement.DoesNotExist:
            # Create a list with todays date twice and no measurement entries
            interval_list = [timezone.now(), timezone.now()]
            measurements_per_interval = [0]
        context["interval_list_js"] = convert_dates_to_js_milliseconds(interval_list)
        context["measurements_per_interval"] = measurements_per_interval
        return context


class RangeInput(NumberInput):
    input_type = "range"
    template_name = "gcampuscore/forms/widgets/range_slider.html"


class ToggleInput(CheckboxInput):
    def get_context(self, name, value, attrs):
        attrs = attrs or {}
        klass = "form-check-input"
        if "class" in attrs:
            klass = " ".join([klass, attrs["class"]])
        attrs.update({"class": klass})
        return super(ToggleInput, self).get_context(name, value, attrs)
