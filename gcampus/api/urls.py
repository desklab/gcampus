#  Copyright (C) 2021 desklab gUG
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

from django.urls import path, include
from rest_framework import routers

from gcampus.api.views import (
    MeasurementAPIViewSet,
    ParameterTypeAPIViewSet,
    ParameterAPIViewSet,
    GeoLookupViewSet,
)

router_v1 = routers.DefaultRouter()
router_v1.register(r"measurements", MeasurementAPIViewSet)
router_v1.register(r"datatypes", ParameterTypeAPIViewSet)
router_v1.register(r"datapoints", ParameterAPIViewSet)
router_v1.register(r"geolookup", GeoLookupViewSet, basename="geolookup")

urlpatterns = [path("", include(router_v1.urls))]

app_name = "gcampusapi"
