from typing import Tuple, List

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.postgres.search import SearchQuery
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.forms import CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _
from django_filters import (
    Filter,
    FilterSet,
    DateTimeFilter,
    CharFilter,
    ModelMultipleChoiceFilter,
)

from gcampus.core.fields import SplitSplitDateTimeField, LocationRadiusField
from gcampus.core.models import DataType
from gcampus.core.models.util import EMPTY


class SplitDateTimeFilter(DateTimeFilter):
    field_class = SplitSplitDateTimeField


class DataTypeFilter(ModelMultipleChoiceFilter):
    def filter(self, qs, value: List[int]):
        datatype_ids = [data_type.id for data_type in value]
        if datatype_ids in EMPTY or None in datatype_ids:
            return qs
        if self.distinct:
            qs = qs.distinct()
        query_name = f"data_points__data_type__pk__in"
        for datatype_id in datatype_ids:
            qs = self.get_method(qs)(**{query_name: [datatype_id]})
        return qs


class MeasurementSearchFilter(CharFilter):
    TSVECTOR_CONF = getattr(settings, "TSVECTOR_CONF")

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        qs = self.get_method(qs)(
            **{self.field_name: SearchQuery(value, config=self.TSVECTOR_CONF)}
        )
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
        query = {query_name: (point, Distance(km=distance))}
        qs = self.get_method(qs)(**query)
        return qs


class MeasurementFilter(FilterSet):
    name = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        help_text=_("Filter either by name or comment"),
        label=_("Filter measurements"),
    )
    time_gt = SplitDateTimeFilter(
        field_name="time",
        lookup_expr="gt",
        help_text=_("Filter for measurements conducted before a specified time"),
    )
    time_lt = SplitDateTimeFilter(
        field_name="time",
        lookup_expr="lt",
        help_text=_("Filter for measurements conducted after a specified time"),
    )
    datatypes = DataTypeFilter(
        field_name="datatype",
        queryset=DataType.objects.all(),
        widget=CheckboxSelectMultiple,
        label=_("Data Type"),
        help_text=_("Filter for measurements containing a specific data type"),
    )
    location = GeolocationFilter(
        field_name="location",
        lookup_expr="distance_lte",
        label=_("Location"),
        help_text=_("Filter by radius after selecting a location"),
    )
