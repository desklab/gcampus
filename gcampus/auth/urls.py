#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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
from gcampus.auth.views import (
    AccessKeyLoginFormView,
    CourseTokenLoginFormView,
    logout,
    RegisterFormView,
    CourseOverviewFormView,
    deactivate_access_key,
    activate_access_key,
    generate_new_access_keys,
)

app_name = GCampusAuthAppConfig.label

# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    # Token
    path("register/", RegisterFormView.as_view(), name="register"),
    path("login/", RedirectView.as_view(permanent=True, pattern_name=f"{app_name}:login-access-key"), name="login"),
    path("login/accesskey/", AccessKeyLoginFormView.as_view(), name="login-access-key"),
    path("login/coursetoken/", CourseTokenLoginFormView.as_view(), name="login-course-token"),
    path('logout/', logout, name="logout"),
    # Course Overview
    path("course/overview", CourseOverviewFormView.as_view(), name="course-overview"),
    path("course/tokens/<int:pk>/deactivate", deactivate_access_key, name="deactivate"),
    path("course/tokens/<int:pk>/activate", activate_access_key, name="activate"),
    path("course/overview/generate", generate_new_access_keys, name="generate-new-access-keys"),
]
# fmt: on
# pylint: enable=line-too-long
