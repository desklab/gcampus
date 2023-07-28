#  Copyright (C) 2023 desklab gUG (haftungsbeschränkt)
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

__all__ = ["urlpatterns", "app_name"]

from django.urls import path, register_converter

from gcampus.map.apps import GCampusMapAppConfig
from gcampus.map.converters import Base64VersionConverter
from gcampus.map.views import cluster_marker

register_converter(Base64VersionConverter, "version")

urlpatterns = [
    path("map/marker/<int:count>/", cluster_marker),
    path("map/marker/<int:count>/<version:version>/", cluster_marker, name="marker"),
]

app_name = GCampusMapAppConfig.label
