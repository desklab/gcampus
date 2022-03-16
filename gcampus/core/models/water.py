#  Copyright (C) 2022 desklab gUG (haftungsbeschränkt)
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

from __future__ import annotations

__all__ = [
    "WaterType",
    "FlowType",
    "Water",
    "OSMElementType",
]

from typing import Optional, List

from django.contrib.gis.db.models import GeometryField
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy

from gcampus.core.models.util import EMPTY, DateModelMixin


class OSMElementType(models.TextChoices):
    NODE = "node", pgettext_lazy("osm node", "node")
    WAY = "way", pgettext_lazy("osm way", "way")
    RELATION = "relation", pgettext_lazy("osm relation", "relation")


class WaterType(models.TextChoices):
    WETLAND = "wetland", gettext_lazy("wetland")
    COASTLINE = "coastline", gettext_lazy("coastline")
    BAY = "bay", gettext_lazy("bay")
    RIVER = "river", gettext_lazy("river")
    STREAM = "stream", gettext_lazy("stream")
    TIDAL_CHANNEL = "tidal_channel", gettext_lazy("tidal channel")
    CANAL = "canal", gettext_lazy("canal")
    DRAIN = "drain", gettext_lazy("drain")
    DITCH = "ditch", gettext_lazy("ditch")
    LAGOON = "lagoon", gettext_lazy("lagoon")
    OXBOW = "oxbow", gettext_lazy("oxbow")
    LAKE = "lake", gettext_lazy("lake")
    BASIN = "basin", gettext_lazy("basin")
    HARBOUR = "harbour", gettext_lazy("harbour")
    POND = "pond", gettext_lazy("pond")
    RESERVOIR = "reservoir", gettext_lazy("reservoir")
    WASTEWATER = "wastewater", gettext_lazy("wastewater")
    SPRING = "spring", gettext_lazy("spring")
    __empty__ = gettext_lazy("unknown")

    @classmethod
    def from_tags(cls, tags: dict) -> Optional[WaterType]:
        """Guess the water type using the provided tags.

        :param tags: Tags provided by OpenStreetMaps. Should include
            keys like 'water', 'waterway' or 'natural'.
        :type tags: dict
        :returns: A water type instance or ``None``.
        :rtype: Optional[WaterType]
        """
        if tags in EMPTY:
            # just skip the checks -> unknown water type
            return None
        water_type: Optional[str] = tags.get("water", None)
        if water_type is None or water_type not in cls:
            # `water` tag not present, use `waterway` tag
            water_type = tags.get("waterway", None)
            if water_type is None or water_type not in cls:
                # No `water*` tag present, use `natural` tag
                water_type = tags.get("natural", None)
        if water_type in cls:
            return cls(water_type)
        return None


_RUNNING_WATER_TYPES: List[WaterType] = [
    WaterType.RIVER, WaterType.STREAM, WaterType.TIDAL_CHANNEL, WaterType.CANAL,
    WaterType.DRAIN, WaterType.DITCH,
]

_STANDING_WATER_TYPES: List[WaterType] = [
    WaterType.WETLAND, WaterType.LAKE, WaterType.BASIN, WaterType.POND,
    WaterType.RESERVOIR, WaterType.LAGOON
]

_UNDECIDED_WATER_TYPES: List[WaterType] = [
    WaterType.COASTLINE, WaterType.BAY, WaterType.OXBOW, WaterType.HARBOUR,
    WaterType.WASTEWATER, WaterType.SPRING
]


class FlowType(models.TextChoices):
    STANDING = "standing", gettext_lazy("standing water")
    RUNNING = "running", gettext_lazy("running water")
    __empty__ = gettext_lazy("unknown")

    @classmethod
    def from_water_type(cls, water_type: WaterType) -> Optional[FlowType]:
        """Guess a water's flow type based on its water type.

        :param water_type: A water type member. If a string is provided,
            the water type is derived from this string.
        :returns: A flow type instance or ``None``
        """
        if not water_type:
            return None
        if isinstance(water_type, str):
            if water_type not in WaterType:
                return None
            water_type = WaterType(water_type)
        if water_type in _RUNNING_WATER_TYPES:
            return cls.RUNNING
        elif water_type in _STANDING_WATER_TYPES:
            return cls.STANDING
        elif water_type in _UNDECIDED_WATER_TYPES:
            # Undecided waters have been introduced for the case that we
            # might want to introduce special logic for that case. For
            # now, these just return None and are thereby undefined.
            return None
        return None


class Water(DateModelMixin):
    class Meta:
        verbose_name = gettext_lazy("Water")
        verbose_name_plural = gettext_lazy("Waters")
        ordering = ("name", "osm_id")

    geometry = GeometryField(
        blank=False,
        verbose_name=gettext_lazy("Geometry")
    )
    tags = models.JSONField(
        default=dict, blank=True, null=False,
        verbose_name=gettext_lazy("Tags")
    )
    osm_id = models.BigIntegerField(
        null=True, verbose_name=gettext_lazy("OpenStreetMap ID")
    )
    osm_element_type = models.CharField(
        choices=OSMElementType.choices, null=False, blank=False, max_length=16,
    )
    flow_type = models.CharField(
        choices=FlowType.choices, null=True, blank=True, max_length=16,
        verbose_name=gettext_lazy("Flow type")
    )
    water_type = models.CharField(
        choices=WaterType.choices, null=True, blank=True, max_length=16,
        verbose_name=gettext_lazy("Water type")
    )
    name = models.CharField(null=False, default="", blank=True, max_length=200)

    _default_water_name: str = gettext_lazy("Unnamed {water_type!s}")

    def save(self, **kwargs):
        if not kwargs.get("update_fields", None):
            # skip if 'update_fields' is provided
            if not self.water_type:
                self.water_type = self.guess_water_type(self.tags)
            if not self.flow_type:
                self.flow_type = self.guess_flow_type(self.water_type)
        return super(Water, self).save(**kwargs)

    @property
    def display_name(self) -> str:
        """Retrieve human-readable name. Defaults to the :attr:`.name`
        field if it is set.

        :returns: The name of the water.
        :rtype: str
        """
        if self.name:
            return self.name
        water_type_str: Optional[str] = self.water_type
        if water_type_str is None:
            return gettext_lazy("Unnamed water")
        return self._default_water_name.format(water_type=water_type_str)

    @staticmethod
    def guess_water_type(tags: dict) -> Optional[WaterType]:
        """Guess the water type using the provided tags.

        :param tags: Tags provided by OpenStreetMaps. Should include
            keys like 'water', 'waterway' or 'natural'.
        :type tags: dict
        :returns: A water type instance or ``None``.
        :rtype: Optional[WaterType]
        """
        return WaterType.from_tags(tags)

    @staticmethod
    def guess_flow_type(water_type: Optional[WaterType]) -> Optional[FlowType]:
        """Guess the flow type (running or standing) using the provided
        water type.

        :param water_type: A member of :class:`.WaterType`.
        :type water_type: Optional[WaterType]
        :returns: A flow type instance or ``None``.
        :rtype: Optional[FlowType]
        """
        return FlowType.from_water_type(water_type)

    def __str__(self):
        return str(self.display_name)

    def __repr__(self):
        return f"Water(pk={self.pk}, osm_id={self.osm_id})"
