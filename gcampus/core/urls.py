from django.urls import path

from gcampus.core.views.measurement import (
    MeasurementFormView,
    DataPointFormSetView,
    MeasurementListView,
    MeasurementDetailView,
    MeasurementSearchResult,
    MeasurementSearch,
)

urlpatterns = [
    path("add/", MeasurementFormView.as_view(), name="add_measurement"),
    path(
        "add/<int:measurement_id>/data/",
        DataPointFormSetView.as_view(),
        name="add_data_points",
    ),
    path("measurements/", MeasurementListView.as_view(), name="measurements"),
    path(
        "measurement/<int:pk>/detail",
        MeasurementDetailView.as_view(),
        name="measurement_detail",
    ),
    path("measurementsearch/", MeasurementSearch.as_view(), name="measurementsearch"),
    path(
        "measurementsearchresult/",
        MeasurementSearchResult.as_view(),
        name="measurementsearchresult",
    ),
]

app_name = "gcampuscore"
