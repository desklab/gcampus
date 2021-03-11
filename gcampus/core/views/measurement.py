from django.views.generic import ListView

from gcampus.core.models import Measurement


class MeasurementList(ListView):
    model = Measurement
