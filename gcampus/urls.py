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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("gcampus.core.urls")),
    path("", include("gcampus.auth.urls")),
    path("", include("gcampus.documents.urls")),
    path("", include("gcampus.analysis.urls")),
    path("api/v1/", include("gcampus.api.urls", namespace="v1")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls"))),

handler403 = "gcampus.auth.views.permission_denied_error_handler"
