from django.urls import path, include

from rest_framework import routers

from gcampus.api.views import (
    MeasurementAPIViewSet,
    DataTypeAPIViewSet,
    DataPointAPIViewSet, GeoLookupViewSet,
)

router_v1 = routers.DefaultRouter()
router_v1.register(r"measurements", MeasurementAPIViewSet)
router_v1.register(r"datatypes", DataTypeAPIViewSet)
router_v1.register(r"datapoints", DataPointAPIViewSet)
router_v1.register(r"geolookup", GeoLookupViewSet, basename="geolookup")

urlpatterns = [path("", include(router_v1.urls))]

app_name = "gcampusapi"
