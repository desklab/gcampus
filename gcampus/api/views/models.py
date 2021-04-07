from rest_framework import generics, viewsets
from rest_framework_gis.pagination import GeoJsonPagination

from gcampus.api.serializers import (
    MeasurementSerializer,
    DataTypeSerializer,
    DataPointSerializer,
)
from gcampus.core.models import Measurement, DataType, DataPoint


class MeasurementAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    pagination_class = GeoJsonPagination


class DataTypeAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = DataType.objects.all()
    serializer_class = DataTypeSerializer


class DataPointAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = DataPoint.objects.all()
    serializer_class = DataPointSerializer
    pagination_class = GeoJsonPagination
