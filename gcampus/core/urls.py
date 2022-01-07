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

from gcampus.core.apps import GCampusCoreAppConfig
from gcampus.auth.views.course_overview import (
    CourseOverviewFormView,
    deactivate_access_key,
    activate_access_key,
    generate_new_access_keys,
)
from gcampus.core.views.measurement import (
    MeasurementCreateView,
    MeasurementListView,
    MeasurementDetailView,
    MeasurementMapView,
    PersonalMeasurementListView,
    CourseMeasurementListView,
    HiddenCourseMeasurementListView,
    MeasurementEditView,
)
from gcampus.core.views.measurement.visibility import show, hide
from gcampus.core.views.parameter import ParameterFormSetView

# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    path("", MeasurementMapView.as_view(), name="mapview"),
    # Add measurement and parameters
    path("add/", MeasurementCreateView.as_view(), name="add_measurement"),
    path("add/<int:pk>/parameters/", ParameterFormSetView.as_view(), name="add_parameters"),
    # Edit measurement and parameters
    path("edit/<int:pk>", MeasurementEditView.as_view(), name="edit_measurement"),
    path("edit/<int:pk>/parameters/", ParameterFormSetView.as_view(), name="edit_parameters"),
    # Measurement list and details
    path("measurement/<int:pk>/delete", MeasurementDeleteView.as_view(), name="measurement-delete"),
    path("measurement/<int:pk>/delete", MeasurementDeleteView.as_view(), name="delete-measurement"),
    path("measurement/<int:pk>/edit/", MeasurementEditView.as_view(), name="edit-measurement"),
    path("measurements/", MeasurementListView.as_view(), name="measurements"),
    path("measurement/<int:pk>", MeasurementDetailView.as_view(), name="measurement_detail"),
    path("personal/measurements", PersonalMeasurementListView.as_view(), name="personal_measurements"),
    path("course/measurements", CourseMeasurementListView.as_view(), name="course_measurements"),
]
# fmt: on
# pylint: enable=line-too-long

app_name = GCampusCoreAppConfig.label
