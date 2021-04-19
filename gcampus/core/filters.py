from typing import Tuple

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.postgres.search import SearchQuery
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.forms import MultiValueField, IntegerField
from django_filters import Filter, FilterSet, DateTimeFilter, BooleanFilter, CharFilter
from leaflet.forms.fields import PointField

from gcampus.core.fields import SplitSplitDateTimeField, LocationRadiusField
from gcampus.core.models import Measurement
from gcampus.core.models.util import EMPTY


class SplitDateTimeFilter(DateTimeFilter):
    field_class = SplitSplitDateTimeField


class HasDataTypeFilter(BooleanFilter):
    field_class = SplitSplitDateTimeField


class MeasurementSearchFilter(CharFilter):

    TSVECTOR_CONF = getattr(settings, "TSVECTOR_CONF")

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        qs = self.get_method(qs)(**{
            self.field_name: SearchQuery(value, config=self.TSVECTOR_CONF)
        })
        return qs


class GeolocationFilter(Filter):
    field_class = LocationRadiusField

    def filter(self, qs: QuerySet, value: Tuple[Point, int]) -> QuerySet:
        if value in EMPTY or None in value:
            return qs
        if self.distinct:
            qs = qs.distinct()
        query_name = f"{self.field_name}__{self.lookup_expr}"
        point, distance = value
        query = {
            query_name: (point, Distance(km=distance))  # TODO variable distance
        }
        qs = self.get_method(qs)(**query)
        return qs


class MeasurementFilter(FilterSet):
    time_gt = SplitDateTimeFilter(field_name='time', lookup_expr="gt")
    time_lt = SplitDateTimeFilter(field_name='time', lookup_expr="lt")
    has_datatype = BooleanFilter(field_name="DataType")
    location = GeolocationFilter(field_name="location", lookup_expr="distance_lte")

    # location = CharFilter(method="filter_location", field_name="GeometryField")

    def filter_location(self, queryset, name, value):
        # TODO value from string to coordinates
        return queryset.filter(**{
            name: value,
        })

    class Meta:
        model = Measurement
        fields = {
            "name": ["icontains"],
        }
