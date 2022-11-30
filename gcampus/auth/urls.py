#  Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.urls import path
from django.views.generic import RedirectView

from gcampus.auth.apps import GCampusAuthAppConfig
from gcampus.auth.forms import AccessKeyForm, CourseTokenForm
from gcampus.auth.views import (
    logout,
    RegisterFormView,
    CourseUpdateView,
    AccessKeyCreateView,
    EmailConfirmationView,
    AccessKeyDeactivationView,
)
from gcampus.auth.views.token import LoginView, AccessKeyFormView, CourseTokenFormView

app_name = GCampusAuthAppConfig.label

# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    # Token
    path("register/", RegisterFormView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/access-key/", AccessKeyFormView.as_view(), name="login-access-key"),
    path("login/course-token/", CourseTokenFormView.as_view(), name="login-course-token"),
    #path("login/", RedirectView.as_view(permanent=True, pattern_name=f"{app_name}:login-access-key"), name="login"),
    #path("login/accesskey/", AccessKeyLoginFormView.as_view(), name="login-access-key"),
    #path("login/coursetoken/", CourseTokenLoginFormView.as_view(), name="login-course-token"),
    path('logout/', logout, name="logout"),
    # Course Overview
    path("course/", CourseUpdateView.as_view(), name="course-update"),
    path("course/acceskeys/", AccessKeyCreateView.as_view(), name="course-access-keys"),
    path("course/acceskeys/<int:pk>/", AccessKeyDeactivationView.as_view(), name="course-access-keys-deactivate"),
    path("email/confirm/<courseidb64>/<token>/", EmailConfirmationView.as_view(), name="email-confirmation"),
]
# fmt: on
# pylint: enable=line-too-long
