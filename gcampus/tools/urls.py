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

from gcampus.tools.apps import GCampusToolsAppConfig
from gcampus.tools.views import (
    ODConverterOverView,
    ODConverterDetailView,
    MeasurementKitOverView,
    ToolsOverView,
)

urlpatterns = [
    path("tools/", ToolsOverView.as_view(), name="tools"),
    path(
        "tools/kits/", MeasurementKitOverView.as_view(), name="measurement-kit-overview"
    ),
    path(
        "tools/kits/<int:pk_kit>/",
        ODConverterOverView.as_view(),
        name="od-converter-overview",
    ),
    path(
        "tools/kits/<int:pk_kit>/convert/<int:pk>/",
        ODConverterDetailView.as_view(),
        name="od-converter",
    ),
]

app_name = GCampusToolsAppConfig.label
