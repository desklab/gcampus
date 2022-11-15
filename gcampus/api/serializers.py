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

from django.urls import reverse
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from gcampus.core.models import Measurement, Parameter, ParameterType, Water


class ParameterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterType
        fields = ("name", "short_name", "unit", "color", "category")


class ParameterSerializer(serializers.ModelSerializer):
    parameter_type = ParameterTypeSerializer(many=False, read_only=True)
    measurement = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Parameter
        fields = ("id", "value", "measurement", "parameter_type")


class SimplifiedWaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = (
            "id",
            "display_name",
            "osm_id",
            "flow_type",
            "display_flow_type",
            "water_type",
            "display_water_type",
        )

    display_name = serializers.CharField(read_only=True)
    display_flow_type = serializers.CharField(
        source="get_flow_type_display", read_only=True
    )
    display_water_type = serializers.CharField(
        source="get_water_type_display", read_only=True
    )


class MeasurementSerializer(GeoFeatureModelSerializer):
    parameters = ParameterSerializer(many=True, read_only=True)
    water = SimplifiedWaterSerializer()
    url = serializers.SerializerMethodField(read_only=True)
    title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Measurement
        geo_field = "location"
        fields = (
            "id",
            "name",
            "title",
            "time",
            "comment",
            "parameters",
            "url",
            "water",
        )

    def get_url(self, obj: Measurement) -> str:  # noqa
        return reverse("gcampuscore:measurement-detail", kwargs=dict(pk=obj.pk))

    def get_title(self, obj: Measurement) -> str:  # noqa
        # Returns the string representation of the measurement
        return str(obj)


class MeasurementListSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Measurement
        geo_field = "location"
        fields = ("id", "location", "water_flow_type", "water_id")

    water_flow_type = serializers.CharField(read_only=True, source="water.flow_type")


class WaterSerializer(GeoFeatureModelSerializer):
    """Water GeoJSON serializer

    Serializer for the :class:`gcampus.core.models.Water` model. The
    output is valid GeoJSON.
    """

    class Meta:
        model = Water
        geo_field = "geometry"
        fields = (
            "id",
            "name",
            "display_name",
            "geometry",
            "bbox",
            "osm_id",
            "tags",
            "flow_type",
            "display_flow_type",
            "water_type",
            "display_water_type",
            "measurements",
        )

    bbox = serializers.SerializerMethodField(read_only=True)

    measurements = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Measurement.objects.all()
    )
    display_name = serializers.CharField(read_only=True)
    display_flow_type = serializers.CharField(
        source="get_flow_type_display", read_only=True
    )
    display_water_type = serializers.CharField(
        source="get_water_type_display", read_only=True
    )

    def get_bbox(self, obj: Water):
        xmin, ymin, xmax, ymax = obj.geometry.extent
        return dict(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)


class WaterListSerializer(serializers.ModelSerializer):
    """Water list serializer

    As some rivers are rather large, querying and serializing their
    geometries is costly. For a simple list, only the important fields
    are returned (no GeoJSON).
    """

    class Meta:
        model = Water
        fields = (
            "id",
            "name",
            "display_name",
            "osm_id",
            "flow_type",
            "display_flow_type",
            "water_type",
            "display_water_type",
        )

    display_name = serializers.CharField(read_only=True)
    display_flow_type = serializers.CharField(
        source="get_flow_type_display", read_only=True
    )
    display_water_type = serializers.CharField(
        source="get_water_type_display", read_only=True
    )
