from django.urls import path

from gcampus.core.views.measurement import (
    MeasurementFormView,
    DataPointFormSetView,
    MeasurementListView
)

urlpatterns = [
    path("add/", MeasurementFormView.as_view(), name="add_measurement"),
    path(
        "add/<measurement_id>/data/",
        DataPointFormSetView.as_view(),
        name="add_data_points",
    ),
    path("measurements/", MeasurementListView.as_view(), name="measurements"),
]

app_name = "gcampuscore"
