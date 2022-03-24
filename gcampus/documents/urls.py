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

from django.urls import path

from gcampus.documents.apps import GCampusDocumentsAppConfig
from gcampus.documents.views.generate_csv import filter_csv_download
from gcampus.documents.views.print import (
    CourseOverviewPDF,
    AccessKeyCombinedPDF,
    MeasurementDetailPDF,
    MeasurementListPDF,
)


# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    path("documents/overview", CourseOverviewPDF.as_view(), name="documents-overview"),
    path("documents/accesskeys_combined", AccessKeyCombinedPDF.as_view(), name="accesskey-combined"),
    path("documents/measurement_detail/<int:pk>", MeasurementDetailPDF.as_view(), name="measurement-detail"),
    path("documents/measurement_list", MeasurementListPDF.as_view(), name="measurement-list"),
    path("documents/measurements", filter_csv_download, name="csv"),
]
# fmt: on
# pylint: enable=line-too-long

app_name = GCampusDocumentsAppConfig.label
