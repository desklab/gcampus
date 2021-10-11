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

from collections import OrderedDict
from decimal import Decimal
from typing import List, Tuple, Union

from django.contrib.gis.geos import LineString, GeometryCollection, GEOSGeometry
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from overpy import Way, Node, Relation, RelationWay
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeoFeatureModelListSerializer,
)

from gcampus.core.models import Measurement, Parameter, ParameterType


class ParameterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterType
        fields = ("name", "unit")


class ParameterSerializer(serializers.ModelSerializer):
    parameter_type = ParameterTypeSerializer(many=False, read_only=True)
    measurement = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Parameter
        fields = ("id", "value", "measurement", "parameter_type")


class MeasurementSerializer(GeoFeatureModelSerializer):
    parameters = ParameterSerializer(many=True, read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Measurement
        geo_field = "location"
        fields = ("id", "name", "time", "comment", "parameters", "url", "title")

    def get_url(self, obj: Measurement) -> str:  # noqa
        return reverse("gcampuscore:measurement_detail", kwargs=dict(pk=obj.pk))

    def get_title(self, obj: Measurement) -> str:  # noqa
        # Returns the string representation of the measurement
        return str(obj)


class OverpassElementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    tags = serializers.JSONField()
    geometry = GeometryField()

    def to_representation(self, instance: Union[Way, Relation]):
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
        geometry_value: GEOSGeometry = self.element_to_geometry(instance)
        feature["geometry"] = geometry_field.to_representation(geometry_value)
        processed_fields.add(geometry_field_name)

        # GeoJSON properties
        tags = dict(instance.tags)
        try:
            name = str(tags.pop("name"))
        except KeyError:
            name = ""  # Empty name if tag ``name`` does not exists
        if name == "" or name is None:
            name = self.get_generic_name(instance)
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

    @classmethod
    def get_generic_name(cls, element: Union[Way, Relation]) -> str:
        available_water_types: dict = {
            # "river": _("Unnamed river %(id)s"),
            "lake": _("Unnamed lake %(id)s"),
            "canal": _("Unnamed canal %(id)s"),
            "reservoir": _("Unnamed reservoir %(id)s"),
            "basin": _("Unnamed basin %(id)s"),
            "stream": _("Unnamed stream %(id)s"),
            "pond": _("Unnamed pond %(id)s"),
            "wetland": _("Unnamed wetland %(id)s"),
        }
        water_type = element.tags.get("water")
        if water_type is not None and water_type in available_water_types:
            return available_water_types[water_type] % {"id": element.id}
        # return _("Unnamed Water %(id)s")
        # Some ways may have duplicate elements (sometimes rivers have
        # additional elements for their shoreline) that should be
        # ignored. There has to be a tradeoff between quality and
        # quantity of the data returned.
        return ""

    @classmethod
    def element_to_geometry(
        cls, element: Union[Way, Relation], *, resolve_missing=True
    ) -> GEOSGeometry:
        if isinstance(element, Way):
            return cls.way_to_geometry(element, resolve_missing=resolve_missing)
        elif isinstance(element, Relation):
            return cls.relation_to_geometry(element, resolve_missing=resolve_missing)
        else:
            raise ValueError(f"Unsupported element type {type(element)}")

    @classmethod
    def way_to_geometry(cls, way: Way, *, resolve_missing=True) -> LineString:
        nodes: List[Node] = way.get_nodes(resolve_missing=resolve_missing)
        coordinates: Tuple[Tuple[Decimal, ...], ...] = tuple(
            (node.lon, node.lat) for node in nodes
        )
        return LineString(coordinates)

    @classmethod
    def relation_to_geometry(
        cls, relation: Relation, *, resolve_missing=True
    ) -> GeometryCollection:
        relation_ways: List[RelationWay] = [
            member for member in relation.members if isinstance(member, RelationWay)
        ]
        ways: List[Way] = [
            relation_way.resolve(resolve_missing=resolve_missing)
            for relation_way in relation_ways
        ]
        line_strings: List[LineString] = [
            cls.way_to_geometry(way, resolve_missing=resolve_missing) for way in ways
        ]
        return GeometryCollection(line_strings)


class GeoLookupSerializer(GeoFeatureModelListSerializer):
    def update(self, instance, validated_data):
        raise NotImplementedError()

    child = OverpassElementSerializer()
