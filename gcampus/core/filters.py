#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Tuple, List, Optional

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.postgres.search import SearchQuery
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.forms import CheckboxSelectMultiple, BooleanField
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_filters import (
    Filter,
    FilterSet,
    DateTimeFilter,
    CharFilter,
    ModelMultipleChoiceFilter,
    BooleanFilter,
    DateRangeFilter,
    DateTimeFromToRangeFilter,
    ModelChoiceFilter,
    DateFromToRangeFilter,
)

from gcampus.auth import session
from gcampus.auth.exceptions import UnauthenticatedError, TokenPermissionError
from gcampus.auth.models.token import TokenType
from gcampus.core.fields import SplitSplitDateTimeField, LocationRadiusField
from gcampus.core.fields.datetime import HistogramDateTimeField
from gcampus.core.fields.personal import ToggleField
from gcampus.core.models import ParameterType
from gcampus.core.models.util import EMPTY


def _get_filter_request(filter_instance: Filter) -> Optional[HttpRequest]:
    if not hasattr(filter_instance, "parent"):
        # No parent instance found, return None instead
        return None
    parent_filter_set: MeasurementFilterSet = getattr(filter_instance, "parent")
    if parent_filter_set is not None:
        return parent_filter_set.request
    else:
        return None


class SplitDateTimeFilter(DateTimeFilter):
    field_class = SplitSplitDateTimeField


class MyCourseFilter(BooleanFilter):
    field_class = ToggleField

    def filter(self, qs, value):
        if value:
            request: HttpRequest = _get_filter_request(self)
            if request is None:
                return qs
            elif not session.is_authenticated(request):
                raise UnauthenticatedError()
            else:
                token = session.get_token(request)
                token_type = session.get_token_type(request)
                if token_type is TokenType.access_key:
                    # This complicated query filters all measurements
                    # 1. that belong to a token
                    #   2. which belongs to a specific parent token
                    #     3. that has an access key
                    #       4. matching with the current access key.
                    qs = self.get_method(qs)(
                        token__parent_token__access_keys__token=token
                    )
                else:
                    qs = self.get_method(qs)(token__parent_token__token=token)
        return qs


class MyMeasurementsFilter(BooleanFilter):
    """Filter all personal measurements

    This filter only returns measurements that have been created with
    the access key of the current user. Consequently, this filter is
    only available to users logged in with an access key.
    """

    field_class = ToggleField

    def filter(self, qs, value: bool):
        """Apply filter

        :param qs: Current query set. Previous filters might be applied
            already.
        :param value: Whether to filter only personal measurements
        :raises UnauthenticatedError: User not authenticated
        :raises TokenPermissionError: Not an access key
        """
        if value:
            request: HttpRequest = _get_filter_request(self)
            if request is None:
                return qs
            elif not session.is_authenticated(request):
                raise UnauthenticatedError()
            elif session.get_token_type(request) is not TokenType.access_key:
                raise TokenPermissionError()
            else:
                token = session.get_token(request)
                qs = self.get_method(qs)(token__token=token)
        return qs


class ParameterTypeFilter(ModelMultipleChoiceFilter):
    def filter(self, qs, value: List[int]):
        parameter_type_ids = [parameter_type.id for parameter_type in value]
        if parameter_type_ids in EMPTY or None in parameter_type_ids:
            return qs
        if self.distinct:
            qs = qs.distinct()
        query_name = f"parameters__parameter_type__pk__in"
        for parameter_type_id in parameter_type_ids:
            qs = self.get_method(qs)(**{query_name: [parameter_type_id]})
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


class DateRange(DateFromToRangeFilter):
    field_class = HistogramDateTimeField


class MeasurementFilterSet(FilterSet):
    name = MeasurementSearchFilter(
        field_name="search_vector",
        label=_("Search"),
        help_text=_("Fulltext search for measurements."),
    )
    time_range = DateRange(
        field_name="time",
        lookup_expr="range",
        label=_("Measurement time range"),
        help_text=_("Filter for measurements conducted in a specified time range."),
    )
    parameter_types = ParameterTypeFilter(
        field_name="parameter_types",
        queryset=ParameterType.objects.all(),
        widget=CheckboxSelectMultiple,
        label=_("Parameter"),
        help_text=_("Filter for measurements containing specific parameters."),
    )
    # location = GeolocationFilter(
    #    field_name="location",
    #    lookup_expr="distance_lte",
    #    label=_("Location"),
    #    help_text=_("Filter by radius after selecting a location"),
    # )
    my_course = MyCourseFilter(
        field_name="my_course",
        label=_("Measurements by your course"),
        help_text=_("Display only measurements that have been conducted by my course."),
    )
    my_measurements = MyMeasurementsFilter(
        field_name="my_measurements",
        label=_("Your Measurements"),
        help_text=_("Display only measurements that have been conducted by me."),
    )
