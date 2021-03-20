from django.urls import path

from gcampus.core.views.measurement import MeasurementFormView, DataPointFormSetView

urlpatterns = [
    path("add/", MeasurementFormView.as_view()),
    path(
        "add/<measurement_id>/data/",
        DataPointFormSetView.as_view(),
        name="data_points_add",
    ),
    path("measurement_list/", MeasurementListView.as_view()),
]

app_name = "gcampuscore"
