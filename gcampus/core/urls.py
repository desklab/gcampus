from django.urls import path

from gcampus.core.views.measurement import (
    MeasurementFormView,
    MeasurementListView,
    MeasurementDetailView,
)
#from gcampus.core.views.datapoint import DatapointDetailView


urlpatterns = [
    path("add/", MeasurementFormView.as_view()),
    path("measurement_list/", MeasurementListView.as_view()),
    path(
        "measurement_detail/<int:pk>", MeasurementDetailView.as_view(), name="measurement-detail"
    ),
]
