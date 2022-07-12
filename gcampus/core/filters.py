#  Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
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
from django.db.models import QuerySet, Q
from django.forms import CheckboxSelectMultiple, BaseForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_filters import (
    Filter,
    FilterSet,
    DateTimeFilter,
    CharFilter,
    ModelMultipleChoiceFilter,
    BooleanFilter,
    DateFromToRangeFilter,
)

from gcampus.auth import session
from gcampus.auth.models.token import TokenType, BaseToken
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


class BooleanNoOpFilter(BooleanFilter):
    field_class = ToggleField

    def filter(self, qs, value):
        return qs


class ParameterTypeFilter(ModelMultipleChoiceFilter):
    def filter(self, qs, value: List[ParameterType]):
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
    form: BaseForm

    def filter_queryset(self, queryset) -> QuerySet:
        queryset = super(MeasurementFilterSet, self).filter_queryset(queryset)
        if self.request and session.is_authenticated(self.request):
            token: BaseToken = self.request.token
            same_course: bool = self.form["same_course"].data
            other_courses: bool = self.form["other_courses"].data

            if not other_courses:
                queryset = queryset.filter(token__course_id=token.course_id)

            if session.get_token_type(self.request) is TokenType.access_key:
                same_access_key: bool = self.form["same_access_key"].data
                if not same_access_key and not same_course:
                    queryset = queryset.exclude(token__course_id=token.course_id)
                elif not same_access_key and same_course:
                    queryset = queryset.exclude(token=token)
                if same_access_key and not same_course:
                    queryset = queryset.filter(
                        # same token OR NOT same course
                        Q(token=token)
                        | ~Q(token__course_id=token.course_id)
                    )
                if same_access_key and same_course:
                    # Nothing to filter
                    pass
            else:
                if not same_course:
                    queryset = queryset.exclude(token__course_id=token.course_id)
        return queryset

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

    same_course = BooleanNoOpFilter(
        field_name="same_course",
        label=_("Measurements by your course"),
        help_text=_("Display measurements that have been conducted by your course."),
    )
    same_access_key = BooleanNoOpFilter(
        field_name="same_access_key",
        label=_("Your Measurements"),
        help_text=_("Display measurements that have been conducted by you."),
    )
    other_courses = BooleanNoOpFilter(
        field_name="other_courses",
        label=_("Other courses"),
        help_text=_("Display measurements conducted by other courses."),
    )
