from django.urls import path

from gcampus.auth.apps import GCampusAuthAppConfig
from gcampus.auth.views.token import (
    SetAccessKeyFormView,
    SetCourseTokenFormView,
    logout,
)

# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    # Token
    path("verify/", SetAccessKeyFormView.as_view(), name="verify"),
    path("verify/accesskey/", SetAccessKeyFormView.as_view(), name="access_key_form"),
    path("verify/coursetoken/", SetCourseTokenFormView.as_view(), name="course_token_form"),
    path('logout/', logout, name="logout"),
]
# fmt: on
# pylint: enable=line-too-long

app_name = GCampusAuthAppConfig.label
