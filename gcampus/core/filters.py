from django_filters import FilterSet, DateFilter, DateTimeFilter, CharFilter
from django.contrib.gis.forms import GeometryField

from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.models import Measurement


class SplitDateTimeFilter(DateTimeFilter):
    field_class = SplitSplitDateTimeField


class MeasurementFilter(FilterSet):
    time_gt = SplitDateTimeFilter(field_name='time', lookup_expr="gt")
    time_lt = SplitDateTimeFilter(field_name='time', lookup_expr="lt")

    #location = CharFilter(method="filter_location", field_name="GeometryField")

    def filter_location(self, queryset, name, value):
        # TODO value from string to coordinates
        return queryset.filter(**{
            name: value,
        })

    class Meta:
        model = Measurement
        fields = {
            "name": ["icontains"],
            "location_name": ["icontains"],

        }
