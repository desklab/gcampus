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
from gcampus.core.views.measurement import (
    MeasurementCreateView,
    MeasurementListView,
    MeasurementDetailView,
    MeasurementMapView,
    MeasurementEditView,
    MeasurementDeleteView,
)
from gcampus.core.views.parameter import ParameterFormSetView

# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    # Index
    path("", MeasurementMapView.as_view(), name="mapview"),
    # Measurement
    path("measurement/add/", MeasurementCreateView.as_view(), name="add-measurement"),
    path("measurement/add/<int:pk>/parameters/", ParameterFormSetView.as_view(), name="add-parameters"),
    path("measurement/<int:pk>/", MeasurementDetailView.as_view(), name="measurement-detail"),
    path("measurement/<int:pk>/delete", MeasurementDeleteView.as_view(), name="delete-measurement"),
    path("measurement/<int:pk>/edit/", MeasurementEditView.as_view(), name="edit-measurement"),
    path("measurement/<int:pk>/edit/parameters/", ParameterFormSetView.as_view(), name="edit-parameters"),
    path("measurements/", MeasurementListView.as_view(), name="measurements"),
]
# fmt: on
# pylint: enable=line-too-long

app_name = GCampusCoreAppConfig.label
