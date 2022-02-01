from django.forms import BooleanField

from gcampus.core.widgets import ToggleInput


class ToggleField(BooleanField):
    widget = ToggleInput