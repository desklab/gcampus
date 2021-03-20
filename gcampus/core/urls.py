from django.urls import path

from gcampus.core.views.measurement import MeasurementFormView, DataPointFormSetView

urlpatterns = [
    path("add/", MeasurementFormView.as_view()),
    path(
        "add/<measurement_id>/data/",
        DataPointFormSetView.as_view(),
        name="data_points_add",
    ),
]

app_name = "gcampuscore"
