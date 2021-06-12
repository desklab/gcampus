from django.urls import path

from gcampus.core.views.datapoint import DataPointFormSetView
from gcampus.core.views.measurement import (
    MeasurementFormView,
    MeasurementListView,
    MeasurementDetailView,
    MeasurementMapView,
)
from gcampus.core.views.token import (
    SetStudentTokenFormView,
    SetTeacherTokenFormView,
    logout,
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
    # Token
    path("verify/student/", SetStudentTokenFormView.as_view(), name="student_token_form"),
    path("verify/teacher/", SetTeacherTokenFormView.as_view(), name="teacher_token_form"),
    path('logout/', logout),
]
# fmt: on
# pylint: enable=line-too-long

app_name = "gcampuscore"
