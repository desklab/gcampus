from django.urls import path

from gcampus.auth.apps import GCampusAuthAppConfig
from gcampus.auth.views.token import (
    SetStudentTokenFormView,
    SetTeacherTokenFormView,
    logout,
)

# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    # Token
    path("verify/", SetStudentTokenFormView.as_view(), name="verify"),
    path("verify/student/", SetStudentTokenFormView.as_view(), name="student_token_form"),
    path("verify/teacher/", SetTeacherTokenFormView.as_view(), name="teacher_token_form"),
    path('logout/', logout, name="logout"),
]
# fmt: on
# pylint: enable=line-too-long

app_name = GCampusAuthAppConfig.label
