import datetime

from django.core.exceptions import ValidationError
from django.forms import DateTimeField, SplitDateTimeField, MultiValueField, IntegerField
from django.forms.utils import from_current_timezone
from django.utils.dateparse import parse_datetime
from leaflet.forms.fields import PointField

from gcampus.core.models.util import EMPTY
from gcampus.core.widgets import SplitSplitDateTimeWidget, LocationRadiusWidget


class SplitSplitDateTimeField(DateTimeField):
    widget = SplitSplitDateTimeWidget

    def to_python(self, value):
        """
        Validate that the input can be converted to a datetime. Return a
        Python datetime.datetime object.
        """
        if value in self.empty_values:
            return None
        if isinstance(value, list):
            if len(value) != 2:
                raise ValueError(
                    "Expected SplitDateTimeWidget to return a list of length 2 but"
                    f" got {len(value)}!"
                )
            date_list = value[0]
            time_list = value[1]
            if len(date_list) != 3:
                raise ValueError(
                    "Expected SplitDateWidget to return a list of length 3 but"
                    f" got {len(date_list)}"
                )
            if len(time_list) != 2:
                raise ValueError(
                    "Expected SplitDateWidget to return a list of length 2 but"
                    f" got {len(date_list)}"
                )
            day, month, year = date_list
            hour, minute = time_list
            try:
                result = datetime.datetime(
                    day=int(day),
                    month=int(month),
                    year=int(year),
                    hour=int(hour),
                    minute=int(minute),
                )
            except (TypeError, ValueError, OverflowError):
                raise ValidationError(self.error_messages["invalid"], code="invalid")
            return from_current_timezone(result)
        return super(SplitSplitDateTimeField, self).to_python(value)


class LocationRadiusField(MultiValueField):
    widget = LocationRadiusWidget

    def compress(self, data_list):
        if data_list in EMPTY:
            return [None, None]
        return data_list

    def __init__(self, *args, **kwargs):
        super(LocationRadiusField, self).__init__(
            (PointField(), IntegerField()), *args, **kwargs
        )