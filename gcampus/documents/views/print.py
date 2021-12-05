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

__all__ = ["CourseOverviewPDF"]

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy

from gcampus.auth import utils
from gcampus.auth.decorators import require_course_token
from gcampus.auth.models import CourseToken
from gcampus.core.models import Measurement
from gcampus.core.models.util import EMPTY
from gcampus.documents.views.generic import SingleObjectDocumentView


class CourseOverviewPDF(SingleObjectDocumentView):
    template_name = "gcampusprint/documents/access_course.html"
    filename = gettext_lazy("gewaessercampus-course-overview.pdf")
    context_object_name = "course_token"
    model = CourseToken

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        token = utils.get_token(self.request)
        return get_object_or_404(queryset, token=token)

    @method_decorator(require_course_token)
    def dispatch(self, request, *args, **kwargs):
        return super(CourseOverviewPDF, self).dispatch(request, *args, **kwargs)

    def get_filename(self):
        if self.object.token_name in EMPTY:
            return self.filename
        return gettext_lazy("gewaessercampus-overview-{course_name:s}.pdf").format(
            course_name=slugify(self.object.token_name)
        )


class AccessKeyCombinedPDF(SingleObjectDocumentView):
    template_name = "gcampusprint/documents/access_student_combined.html"
    filename = gettext_lazy("gewaessercampus-accesskey-combined.pdf")
    context_object_name = "course_token"
    model = CourseToken

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        token = utils.get_token(self.request)
        return get_object_or_404(queryset, token=token)

    @method_decorator(require_course_token)
    def dispatch(self, request, *args, **kwargs):
        return super(AccessKeyCombinedPDF, self).dispatch(request, *args, **kwargs)

    def get_filename(self):
        if self.object.token_name in EMPTY:
            return self.filename
        return gettext_lazy(
            "gewaessercampus-accesskey-combined-{course_name:s}.pdf"
        ).format(course_name=slugify(self.object.token_name))


class MeasurementDetailPDF(SingleObjectDocumentView):
    template_name = "gcampusprint/documents/measurement_detail.html"
    filename = gettext_lazy("gewaessercampus-measurement-detail.pdf")
    context_object_name = "measurement"
    model = Measurement

    @method_decorator(require_course_token)
    def dispatch(self, request, *args, **kwargs):
        return super(MeasurementDetailPDF, self).dispatch(request, *args, **kwargs)

    def get_filename(self):
        if self.object.name in EMPTY:
            return self.filename
        return gettext_lazy("gewaessercampus-measurement-detail-{name:s}.pdf").format(
            name=slugify(self.object.name)
        )
