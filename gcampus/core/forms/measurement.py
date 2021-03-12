from django.forms import ModelForm
from leaflet.forms.widgets import LeafletWidget

from gcampus.core.models import Measurement


class MeasurementForm(ModelForm):
    class Meta:
        model = Measurement
        fields = ["name", "time", "location", "comment"]
        widgets = {"location": LeafletWidget()}
