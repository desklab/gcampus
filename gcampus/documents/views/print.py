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

__all__ = [
    "CourseOverviewPDF",
    "AccessKeyCombinedPDF",
    "MeasurementDetailPDF",
    "MeasurementListPDF",
]

import base64
from typing import Tuple, List

from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Point
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy

from gcampus.auth.decorators import require_course_token
from gcampus.auth.models import Course
from gcampus.core.filters import MeasurementFilterSet
from gcampus.core.models import Measurement
from gcampus.core.models.util import EMPTY
from gcampus.documents.views.generic import (
    SingleObjectDocumentView,
    ListDocumentView,
    CachedDocumentView,
)
from gcampus.map.static import get_static_map


class CourseOverviewPDF(CachedDocumentView):
    template_name = "gcampusdocuments/documents/access_course.html"
    filename = gettext_lazy("gewaessercampus-course.pdf")
    context_object_name = "course"
    model = Course
    model_file_field = "overview_document"

    def get_object(self, queryset=None):
        return self.request.token.course

    @method_decorator(require_course_token)
    def dispatch(self, request, *args, **kwargs):
        return super(CourseOverviewPDF, self).dispatch(request, *args, **kwargs)

    def get_filename(self):
        if self.object.name in EMPTY:
            return self.filename
        return gettext_lazy("gewaessercampus-{course_name!s}.pdf").format(
            course_name=slugify(self.object.name)
        )


class AccessKeyCombinedPDF(SingleObjectDocumentView):
    template_name = "gcampusdocuments/documents/access_student_combined.html"
    filename = gettext_lazy("gewaessercampus-access-keys.pdf")
    context_object_name = "course"
    model = Course

    def get_object(self, queryset=None):
        return self.request.token.course

    @method_decorator(require_course_token)
    def dispatch(self, request, *args, **kwargs):
        return super(AccessKeyCombinedPDF, self).dispatch(request, *args, **kwargs)

    def get_filename(self):
        if self.object.name in EMPTY:
            return self.filename
        return gettext_lazy("{course_name!s}-access-keys.pdf").format(
            course_name=slugify(self.object.name)
        )


class MeasurementDetailPDF(CachedDocumentView):
    template_name = "gcampusdocuments/documents/measurement_detail.html"
    filename = gettext_lazy("gewaessercampus-measurement-detail.pdf")
    context_object_name = "measurement"
    model = Measurement
    model_file_field = "document"
    object: Measurement

    def get_context_data(self, **kwargs):
        map_bytes: bytes
        map_bytes, _ = get_static_map(
            [self.object.location], center=self.object.location.tuple
        )
        kwargs["map"] = f"data:image/png;base64,{base64.b64encode(map_bytes).decode()}"
        return super(MeasurementDetailPDF, self).get_context_data(**kwargs)

    def get_filename(self):
        if self.object.name in EMPTY:
            return self.filename
        return gettext_lazy("gewaessercampus-measurement-detail-{name:s}.pdf").format(
            name=slugify(self.object.name)
        )


class MeasurementListPDF(ListDocumentView):
    template_name = "gcampusdocuments/documents/measurement_list.html"
    filename = gettext_lazy("gewaessercampus-measurement-list.pdf")
    context_object_name = "measurements"
    model = Measurement
    queryset = (
        Measurement.objects.order_by("time")
        .prefetch_related("parameters")
        .prefetch_related("parameters__parameter_type")
        .select_related("water")
        .only(
            "id",
            "location",
            "time",
            "water_id",
            "water__flow_type",
            "water__water_type",
            "water__name",
            "parameters__value",
            "parameters__parameter_type__name",
            "parameters__parameter_type__unit",
        )
    )
    filter: MeasurementFilterSet

    def get_bbox(self) -> Tuple[float, float, float, float]:
        qs = self.get_queryset().all()  # creates a copy of the qs
        aggregation_result = qs.aggregate(bbox=Extent("location"))
        return aggregation_result["bbox"]

    def get_queryset(self) -> QuerySet:
        if not hasattr(self, "filter"):
            self.filter = MeasurementFilterSet(
                self.request.GET,
                queryset=super(MeasurementListPDF, self).get_queryset(),
                request=self.request,
            )
        self.queryset = self.filter.qs
        return super(MeasurementListPDF, self).get_queryset()

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                queryset, page_size
            )
            context = {
                "paginator": paginator,
                "page_obj": page,
                "is_paginated": is_paginated,
                "object_list": queryset,
            }
        else:
            context = {
                "paginator": None,
                "page_obj": None,
                "is_paginated": False,
                "object_list": queryset,
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        simple_queryset = queryset.all().prefetch_related(None)
        kwargs["measurement_count"] = simple_queryset.all().count()
        kwargs["water_count"] = (
            simple_queryset.all().only("water").order_by().distinct("water").count()
        )
        time_query = simple_queryset.all().only("time").values_list("time", flat=True)
        kwargs["time_first"] = time_query.all().earliest("time")
        kwargs["time_last"] = time_query.all().latest("time")

        points: List[Point] = simple_queryset.all().values_list("location", flat=True)
        map_bytes: bytes
        clustered: bytes

        map_bytes, clustered = get_static_map(
            points,
            bbox=(self.get_bbox() if len(points) > 1 else None),
            center=(points[0].tuple if len(points) == 1 else None),
        )
        kwargs["map"] = f"data:image/png;base64,{base64.b64encode(map_bytes).decode()}"
        kwargs["clustered"] = clustered
        context.update(kwargs)
        return super().get_context_data(**context)
