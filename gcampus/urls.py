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

from importlib.util import find_spec

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("gcampus.core.urls")),
    path("", include("gcampus.auth.urls")),
    path("", include("gcampus.documents.urls")),
    path("", include("gcampus.tools.urls")),
    path("", include("gcampus.export.urls")),
    path("", include("gcampus.map.urls")),
    path("api/v1/", include("gcampus.api.urls", namespace="v1")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG and find_spec("debug_toolbar"):
    # Only add debug toolbar urls if the module is present
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls"))),

handler403 = "gcampus.auth.views.permission_denied_error_handler"
