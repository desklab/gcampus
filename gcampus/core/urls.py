from django.urls import path

from gcampus.core.views.measurement import (
    MeasurementFormView,
    DataPointFormSetView,
    MeasurementListView,
    MeasurementDetailView,
    MeasurementMapView,
)
from gcampus.core.views.token import SetStudentTokenFormView, SetTeacherTokenFormView, logout

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
    path(
        "mapview/",
        MeasurementMapView.as_view(),
        name="measurement_mapview",
    ),
    path(
        "verify/student/",
        SetStudentTokenFormView.as_view(),
        name="student_token_form",
    ),
    path(
        "verify/teacher/",
        SetTeacherTokenFormView.as_view(),
        name="teacher_token_form",
    ),
    path('logout/', logout),
]

app_name = "gcampuscore"
