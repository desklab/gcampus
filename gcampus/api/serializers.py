from collections import OrderedDict
from decimal import Decimal
from typing import List, Tuple

from django.contrib.gis.geos import LineString
from overpy import Way, Node
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeoFeatureModelListSerializer,
)

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
        feature = OrderedDict({"type": "Feature"})
        processed_fields = set()

        id_field_name = "id"
        id_field = self.fields[id_field_name]
        id_value = instance.id
        feature["id"] = id_field.to_representation(id_value)
        processed_fields.add(id_field_name)

        geometry_field_name = "geometry"
        geometry_field = self.fields[geometry_field_name]
        geometry_value = self.way_to_geometry(instance)
        feature["geometry"] = geometry_field.to_representation(geometry_value)
        processed_fields.add(geometry_field_name)

        # GeoJSON properties
        tags = dict(instance.tags)
        try:
            name = str(tags.pop("name"))
        except KeyError:
            name = ""  # Empty name if tag ``name`` does not exists
        name_field: serializers.CharField = self.fields["name"]
        tags_field: serializers.JSONField = self.fields["tags"]
        feature["properties"] = {
            "name": name_field.to_representation(name),
            "tags": tags_field.to_representation(tags),
        }
        return feature

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()

    @staticmethod
    def way_to_geometry(way: Way, resolve_missing=True) -> LineString:
        nodes: List[Node] = way.get_nodes(resolve_missing=resolve_missing)
        coordinates: Tuple[Tuple[Decimal, ...], ...] = tuple(
            (node.lon, node.lat) for node in nodes
        )
        return LineString(coordinates)


class GeoLookupSerializer(GeoFeatureModelListSerializer):
    child = OverpassWaySerializer()
