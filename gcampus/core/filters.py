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

from typing import List, Optional, Set, Tuple

from django.conf import settings
from django.contrib.postgres.search import SearchQuery
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, Q
from django.forms import CheckboxSelectMultiple, BaseForm, Select
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
    ChoiceFilter,
    MultipleChoiceFilter,
)

from gcampus.auth import session
from gcampus.auth.models.token import TokenType, BaseToken
from gcampus.core.fields import SplitSplitDateTimeField
from gcampus.core.fields.datetime import HistogramDateTimeField
from gcampus.core.fields.personal import ToggleField
from gcampus.core.models import ParameterType
from gcampus.core.models.util import EMPTY
from gcampus.core.models.water import FlowType, WaterType, Water
from gcampus.core.widgets import DropdownMultipleSelect

WATER_TYPES = (
    (WaterType.RIVER.value, WaterType.RIVER.label),
    (WaterType.STREAM.value, WaterType.STREAM.label),
    (WaterType.TIDAL_CHANNEL.value, WaterType.TIDAL_CHANNEL.label),
    (WaterType.CANAL.value, WaterType.CANAL.label),
    (WaterType.DRAIN.value, WaterType.DRAIN.label),
    (WaterType.DITCH.value, WaterType.DITCH.label),
    (WaterType.WETLAND.value, WaterType.WETLAND.label),
    (WaterType.LAKE.value, WaterType.LAKE.label),
    (WaterType.BASIN.value, WaterType.BASIN.label),
    (WaterType.POND.value, WaterType.POND.label),
    (WaterType.RESERVOIR.value, WaterType.RESERVOIR.label),
    (WaterType.LAGOON.value, WaterType.LAGOON.label),
    (WaterType.COASTLINE.value, WaterType.COASTLINE.label),
    (WaterType.BAY.value, WaterType.BAY.label),
    (WaterType.OXBOW.value, WaterType.OXBOW.label),
    (WaterType.HARBOUR.value, WaterType.HARBOUR.label),
    (WaterType.WASTEWATER.value, WaterType.WASTEWATER.label),
    (WaterType.SPRING.value, WaterType.SPRING.label),
)


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


class WaterTypeFilter(ModelMultipleChoiceFilter):
    def filter(self, qs, value: List[WaterType]):
        water_type_ids = [water_type.id for water_type in value]
        if water_type_ids in EMPTY or None in water_type_ids:
            return qs
        if self.distinct:
            qs = qs.distinct()
        query_name = f"water_type__pk__in"
        for WATER_type_id in water_type_ids:
            qs = self.get_method(qs)(**{query_name: [WATER_type_id]})
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


class DateRange(DateFromToRangeFilter):
    field_class = HistogramDateTimeField


class WaterFilterSet(FilterSet):
    form: BaseForm

    water_type = MultipleChoiceFilter(
        choices=WATER_TYPES, widget=CheckboxSelectMultiple
    )

    class Meta:
        model = Water
        fields = ["water_type"]

    flow_type = ChoiceFilter(
        field_name="flow_type",
        null_label=FlowType.__empty__,
        widget=Select(attrs={"class": "form-select form-select-sm"}),
        choices=(
            (FlowType.RUNNING.value, FlowType.RUNNING.label),
            (FlowType.STANDING.value, FlowType.STANDING.label),
        ),
    )


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

    def get_status(self) -> bool:
        """Get Filter Status

        This function takes a list of new filters and returns a bool
        corresponding to the status of the filter

        :returns: Bool if filter is set
        """
        applied_filters: Set[str] = set(self.form.changed_data)
        # Ignore the name (search field) as it is seperated in the UI
        # from the other filter fields.
        applied_filters -= {"name"}
        if self.request and session.is_authenticated(self.request):
            if self.form["other_courses"].value():
                applied_filters -= {"other_courses"}
            else:
                applied_filters |= {"other_courses"}
            if self.form["same_course"].value():
                applied_filters -= {"same_course"}
            else:
                applied_filters |= {"same_course"}
            if session.get_token_type(self.request) is TokenType.access_key:
                if self.form["same_access_key"].value():
                    applied_filters -= {"same_access_key"}
                else:
                    applied_filters |= {"same_access_key"}

        return len(applied_filters) != 0

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
        widget=CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label=_("Parameter"),
        help_text=_("Filter for measurements containing specific parameters."),
    )
    flow_type = ChoiceFilter(
        field_name="water__flow_type",
        null_label=FlowType.__empty__,
        widget=Select(attrs={"class": "form-select form-select-sm"}),
        choices=(
            (FlowType.RUNNING.value, FlowType.RUNNING.label),
            (FlowType.STANDING.value, FlowType.STANDING.label),
        ),
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
