from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework_gis.pagination import GeoJsonPagination

from gcampus.api.serializers import (
    MeasurementSerializer,
    DataTypeSerializer,
    DataPointSerializer,
)
from gcampus.core.models import Measurement, DataType, DataPoint


class MeasurementAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = Measurement.objects.order_by('time').all()
    serializer_class = MeasurementSerializer
    pagination_class = GeoJsonPagination


class DataTypeAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = DataType.objects.order_by('name').all()
    serializer_class = DataTypeSerializer
    pagination_class = PageNumberPagination


class DataPointAPIViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    queryset = DataPoint.objects.order_by('measurement__time').all()
    serializer_class = DataPointSerializer
    pagination_class = PageNumberPagination
