from django.views.generic import DetailView

from gcampus.core.models import DataPoint


class DatapointDetailView(DetailView):
    model = DataPoint
