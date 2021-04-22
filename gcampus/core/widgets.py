import datetime
from typing import Optional

from django.forms import MultiWidget, NumberInput
from django.forms.utils import to_current_timezone
from django.utils.translation import gettext as _
from django.utils.translation import pgettext
from leaflet.forms.widgets import LeafletWidget


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
        return [None, None]


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


class RangeInput(NumberInput):
    input_type = "range"
    template_name = "gcampuscore/forms/widgets/range_slider.html"



class LocationRadiusWidget(MultiWidget):
    template_name = "gcampuscore/forms/widgets/locationradius.html"
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

        Replicates the functionality of the private method
        :meth:`leaflet.forms.widgets.LeafletWidget._get_attr` which
        provides additional context variables used to render a leaflet
        map.

        .. todo:: Consider calling the private method ``_get_attrs``
            instead.

        :param name: Widget name
        :param attrs: Additional attributes
        :return: Dictionary of additional attributes
        :rtype: dict
        """
        return self.map_widget._get_attrs(name)  # noqa

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
