__ALL__ = ["LocationRadiusField"]

from django.forms import MultiValueField, IntegerField
from leaflet.forms.fields import PointField

from gcampus.core.models.util import EMPTY
from gcampus.core.widgets import LocationRadiusWidget


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
