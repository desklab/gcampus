from collections import OrderedDict
from typing import List

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, \
    GeoFeatureModelListSerializer
from rest_framework_gis.fields import GeometryField
from overpy import Way

from gcampus.core.models import Measurement, DataPoint, DataType


class DataTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataType
        fields = ("name", "unit")


class DataPointSerializer(serializers.HyperlinkedModelSerializer):
    data_type = DataTypeSerializer(many=False, read_only=True)

    class Meta:
        model = DataPoint
        fields = ("id", "value", "measurement", "data_type")


class MeasurementSerializer(GeoFeatureModelSerializer):
    data_points = DataPointSerializer(many=True, read_only=True)

    class Meta:
        model = Measurement
        geo_field = "location"
        fields = ("id", "name", "time", "comment", "data_points")


class OverpassWaySerializer(serializers.Serializer):
    """
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    tags = serializers.JSONField()
    geometry = GeometryField()

    def to_representation(self, instance: Way):
        """
        This method is heavily inspired by
        :class:`rest_framework_gis.serializers.GeoFeatureModelSerializer`

        Copyright (C) 2013-2014 Douglas Meehan
        Licensed under the MIT License
        """
        if isinstance(instance, dict) or instance is None:
            return instance
        feature = OrderedDict({
            "type": "Feature"
        })
        processed_fields = set()

        id_field_name = "id"
        id_field = self.fields[id_field_name]
        id_value = instance.id
        feature["id"] = id_field.to_representation(id_value)
        processed_fields.add(id_field_name)

        geometry_field_name = "geometry"
        geometry_field = self.fields[geometry_field_name]
        geometry_value = instance.nodes
        feature["geometry"] = geometry_field.to_representation(geometry_value)
        processed_fields.add(geometry_field_name)

        fields = [
            field_value
            for field_key, field_value in self.fields.items()
            if field_key not in processed_fields
        ]

        # GeoJSON properties
        feature["properties"] = self.get_properties(instance, fields)

    def get_properties(self, instance, fields):
        """
        This method is heavily inspired by
        :class:`rest_framework_gis.serializers.GeoFeatureModelSerializer`

        Copyright (C) 2013-2014 Douglas Meehan
        Licensed under the MIT License
        """
        properties = OrderedDict()

        for field in fields:
            if field.write_only:
                continue
            value = field.get_attribute(instance)
            representation = None
            if value is not None:
                representation = field.to_representation(value)
            properties[field.field_name] = representation

        return properties

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()


class GeoLookupSerializer(GeoFeatureModelListSerializer):
    child = OverpassWaySerializer()
