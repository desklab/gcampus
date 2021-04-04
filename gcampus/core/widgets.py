import datetime
from typing import Optional

from django.forms import MultiWidget, NumberInput
from django.forms.utils import to_current_timezone
from django.utils.translation import gettext as _
from django.utils.translation import pgettext


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
            "placeholder": pgettext("hour input short", "HH")
        }
        minute_attrs = {
            "title": _("Minute"),
            "maxlength": 2,
            "min": 0,
            "max": 59,
            "placeholder": pgettext("minute input short", "MM")
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
            "placeholder": pgettext("day input short", "DD")
        }
        month_attrs = {
            "title": _("Month"),
            "maxlength": 2,
            "min": 1,
            "max": 12,
            "placeholder": pgettext("month input short", "MM")
        }
        year_attrs = {
            "maxlength": 4,
            "title": _("Year"),
            "placeholder": pgettext("year input short", "YYYY")
        }
        day_attrs.update(attrs)
        month_attrs.update(attrs)
        year_attrs.update(attrs)
        widgets = (
            NumberInput(attrs=day_attrs),
            NumberInput(attrs=month_attrs),
            NumberInput(attrs=year_attrs)
        )
        self.date_format = date_format
        super().__init__(widgets)

    def decompress(self, value: datetime.date):
        if value:
            return [f"{value.day:02d}", f"{value.month:02d}", f"{value.year:02d}"]
        return [None, None]


class SplitSplitDateTimeWidget(MultiWidget):
    """
    A widget that splits datetime input into two <input type="text"> boxes.
    """
    supports_microseconds = False
    template_name = 'gcampuscore/forms/widgets/splitsplitdatetime.html'

    def __init__(self, attrs=None, date_format=None, time_format=None, date_attrs=None, time_attrs=None):
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
