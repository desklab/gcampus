from django.urls import path

from gcampus.core.apps import GCampusCoreAppConfig
from gcampus.core.views.datapoint import DataPointFormSetView
from gcampus.core.views.measurement import (
    MeasurementFormView,
    MeasurementListView,
    MeasurementDetailView,
    MeasurementMapView, PersonalMeasurementListView,
)

# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    path("", MeasurementMapView.as_view(), name="mapview"),
    # Add measurement and data
    path("add/", MeasurementFormView.as_view(), name="add_measurement"),
    path("add/<int:measurement_id>/data/", DataPointFormSetView.as_view(), name="add_data_points"),
    # Edit measurement and data
    # TODO @jnsdrtlf: editable measurement form
    # path("edit/<int:measurement_id>", MeasurementFormView.as_view(), name="edit_measurement"),
    path("edit/<int:measurement_id>/data/", DataPointFormSetView.as_view(), name="edit_data_points"),
    # Measurement list and details
    path("measurements/", MeasurementListView.as_view(), name="measurements"),
    path("measurement/<int:pk>/detail", MeasurementDetailView.as_view(), name="measurement_detail"),
    path("personal/measurements", PersonalMeasurementListView.as_view(), name="personal_measuremets"),
]
# fmt: on
# pylint: enable=line-too-long

app_name = GCampusCoreAppConfig.label
