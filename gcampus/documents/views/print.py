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

    def dispatch(self, request, *args, **kwargs):
        return super(MeasurementDetailPDF, self).dispatch(request, *args, **kwargs)

    def get_filename(self):
        if self.object.name in EMPTY:
            return self.filename
        return gettext_lazy("gewaessercampus-measurement-detail-{name:s}.pdf").format(
            name=slugify(self.object.name)
        )


class MeasurementAssessmentPDF(SingleObjectDocumentView):
    template_name = "gcampusdocuments/documents/measurement_assessment.html"
    filename = gettext_lazy("gewaessercampus-measurement-assessment.pdf")
    context_object_name = "measurement"
    model = Measurement

    def dispatch(self, request, *args, **kwargs):
        return super(MeasurementAssessmentPDF, self).dispatch(request, *args, **kwargs)

    def get_filename(self):
        if self.object.name in EMPTY:
            return self.filename
        return gettext_lazy(
            "gewaessercampus-measurement-assessment-{name:s}.pdf"
        ).format(name=slugify(self.object.name))


class MeasurementListPDF(ListDocumentView):
    template_name = "gcampusdocuments/documents/measurement_list.html"
    filename = gettext_lazy("gewaessercampus-measurement-list.pdf")
    context_object_name = "measurements"
    model = Measurement

    def bounding_box(self):
        # TODO: dirty proof of concept, fix
        long_max = (
            self.object_list.order_by("time").values_list("location")[0][0].coords[0]
        )
        long_min = (
            self.object_list.order_by("time").values_list("location")[0][0].coords[0]
        )
        lat_max = (
            self.object_list.order_by("time").values_list("location")[0][0].coords[1]
        )
        lat_min = (
            self.object_list.order_by("time").values_list("location")[0][0].coords[1]
        )
        for measurement in self.object_list.order_by("time"):
            coords = measurement.location.coords
            if coords[0] > long_max:
                long_max = coords[0]
            if coords[0] < long_min:
                long_min = coords[0]
            if coords[1] > lat_max:
                lat_max = coords[1]
            if coords[1] < lat_min:
                lat_min = coords[1]
        return long_min, long_max, lat_min, lat_max

    def map_overlay(self):
        marker_list = ""
        for measurement in self.object_list:
            marker_list += (
                "pin-l+083973("
                + str(measurement.location.coords[0])
                + ","
                + str(measurement.location.coords[1])
                + "),"
            )
        marker_list = marker_list[:-1]
        return marker_list

    def get_queryset(self):
        queryset = super(MeasurementListPDF, self).get_queryset()
        filterset = MeasurementFilterSet(
            self.request.GET, queryset=queryset, request=self.request
        )
        return filterset.qs

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
        kwargs["measurement_count"] = queryset.count()
        kwargs["water_count"] = (
            queryset.only("water").order_by().distinct("water").count()
        )
        kwargs["time_first"] = (
            queryset.only("time").values_list("time", flat=True).earliest("time")
        )
        kwargs["time_last"] = (
            queryset.only("time").values_list("time", flat=True).latest("time")
        )
        bbox = self.bounding_box()
        kwargs["bbox_long_min"] = bbox[0]
        kwargs["bbox_long_max"] = bbox[1]
        kwargs["bbox_lat_min"] = bbox[2]
        kwargs["bbox_lat_max"] = bbox[3]
        kwargs["map_overlay"] = self.map_overlay()
        context.update(kwargs)
        return super().get_context_data(**context)
