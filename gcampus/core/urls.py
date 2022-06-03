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
from gcampus.core.views.water import WaterListView, WaterDetailView

# uncomment to test 404 and 500 pages locally
# from django.views.defaults import page_not_found, server_error
# def custom_page_not_found(request):
#    return page_not_found(request, None)
#
# def custom_server_error(request):
#    return server_error(request)

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
    path("waters/", WaterListView.as_view(), name="waters"),
    path("water/<int:pk>/", WaterDetailView.as_view(), name="water-detail"),
    # path("404/", custom_page_not_found), # uncomment to test 404 page locally
    # path("500/", custom_server_error), # uncomment to test 500 page locally
]
# fmt: on
# pylint: enable=line-too-long

app_name = GCampusCoreAppConfig.label
