from django_filters import FilterSet, DateFilter
from .models import Measurement

# from wagtail.search import index


class MeasurementFilter(FilterSet):
    class Meta:
        model = Measurement
        fields = {"name": ["icontains"], "location_name": ["icontains"]}
