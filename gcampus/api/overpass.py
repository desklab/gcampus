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

"""Overpass JSON API client

Simplified Overpass API client that only works with the default JSON
output format. It is inspired by the overpy client.

Designed for GewaesserCampus' water lookup.
"""

__all__ = [
    "Element",
    "Node",
    "Way",
    "Relation",
    "query",
    "OverpassParseError",
]
__author__ = "Jonas Drotleff <j.drotleff@desk-lab.de>"

import abc
from dataclasses import dataclass
from typing import Optional, List, Tuple

import requests
from django.conf import settings
from django.contrib.gis.geos import (
    GEOSGeometry,
    MultiPolygon,
    Polygon,
    LineString,
    LinearRing,
    Point,
    GeometryCollection,
    MultiLineString,
)

from gcampus.core.models import Water
from gcampus.core.models.water import OSMElementType


@dataclass
class Element(abc.ABC):
    """Elements are the basic building blocks of an overpass response.
    An element can be either a node, a way (collection of nodes) or a
    relation (collection of ways and nodes).

    This class is the base for all three of the elements mentioned above
    and provides an interface to common data attributes.
    """

    osm_id: int
    tags: dict
    geometry: Optional[GEOSGeometry] = None

    def get_element_type(self) -> OSMElementType:
        raise NotImplementedError()

    def to_water(self) -> Water:
        # Use german name by default
        name: str = self.tags.get("name:de", "")
        if name == "":
            # Fall back to international name
            name = self.tags.get("name", "")
        return Water(
            osm_id=self.osm_id, tags=self.tags, geometry=self.geometry, name=name,
            osm_element_type=self.get_element_type()
        )


@dataclass
class Node(Element):
    def get_element_type(self) -> OSMElementType:
        return OSMElementType.NODE


@dataclass
class Way(Element):
    def get_element_type(self) -> OSMElementType:
        return OSMElementType.WAY


@dataclass
class Relation(Element):
    def get_element_type(self) -> OSMElementType:
        return OSMElementType.RELATION


def _object_hook(obj: dict):
    keys = obj.keys()
    if "type" not in keys or "ref" in keys or "role" in keys:
        # Ignore object as it is not an element.
        # 'ref' and 'role' are used as they are common for relation
        # members (which do have a 'type').
        return obj
    element_type = obj["type"]
    if element_type not in ["node", "way", "relation"]:
        # Unknown type. Maybe `obj` is a list of tags.
        return obj
    osm_id: Optional[int] = obj.get("id", None)
    if osm_id is None:
        # Fail gracefully if no ID is present.
        return obj
    tags: dict = obj.get("tags", {})
    if element_type == "node":
        if "lon" not in keys or "lat" not in keys:
            return obj
        geometry = Point(obj["lon"], obj["lat"])
        return Node(osm_id, tags, geometry)
    elif element_type == "way":
        if "geometry" not in keys:
            return obj
        geometry = LineString([(geom["lon"], geom["lat"]) for geom in obj["geometry"]])
        return Way(osm_id, tags, geometry)
    else:
        if "members" not in keys:
            return obj
        # List of inner rings (e.g. for a lake this would be an island)
        inner: List[LinearRing] = []
        # List of outer rings (e.g. for a lake this would be the
        # shoreline)
        outer: List[LinearRing] = []
        # Everything else. For rivers and streams this is typically
        # a list of line strings representing the waterway.
        other: List[LineString] = []
        for member in obj["members"]:
            if member.get("type") != "way":
                # Ignore all members that are not ways
                continue
            line_string: List[Tuple[float, float]] = [
                (geom["lon"], geom["lat"]) for geom in member["geometry"]
            ]
            role = member.get("role")
            if role == "inner":
                inner.append(LinearRing(line_string))
            elif role == "outer":
                outer.append(LinearRing(line_string))
            else:
                other.append(LineString(line_string))
        if len(outer) > 0:
            # Construct polygons for each outer ring and subtract all
            # inner rings. Merge all polygons into a multi polygon
            polygons = MultiPolygon([Polygon(o, inner) for o in outer])
            if len(other) > 0:
                # Add other geometries and create a geometry collection
                geometry = GeometryCollection([MultiLineString(other), polygons])
            else:
                geometry = polygons
        elif len(other) > 0:
            geometry = MultiLineString(other)
        else:
            # Somehow there were no useful geometries. This could be the
            # case if e.g. the only members were nodes or 'inner' ways.
            # Cases like these are ignored. Return the raw object
            # instead.
            return obj
        return Relation(osm_id, tags, geometry)


def _parse(response: requests.Response, **kwargs) -> List[Element]:
    if "object_hook" not in kwargs:
        kwargs["object_hook"] = _object_hook
    json_result = response.json(**kwargs)
    return [
        element
        for element in json_result.get("elements", [])
        if isinstance(element, Element)
    ]


def query(
    overpass_query: str,
    *,
    endpoint: Optional[str] = None,
    **parse_kwargs,
) -> List[Element]:
    """Query Overpass API

    :param overpass_query: Query string for Overpass. Should always
        include the ``[out:json]`` tag.
    :type overpass_query: str
    :param endpoint: URL endpoint. If ``None``, the endpoint configured
        in the Django settings is used. Defaults to
        ``https://overpass-api.de/api/interpreter``.
    :type endpoint: Optional[str]
    :param parse_kwargs: Additional keyword arguments passed to the
        ``_parse`` function.
    :returns: List of all elements
    :rtype: List[Element]
    :raises requests.exceptions.JSONDecodeError: If response is not JSON
    """
    if endpoint is None:
        endpoint = getattr(
            settings, "OVERPASS_SERVER", "https://overpass-api.de/api/interpreter"
        )
    response: requests.Response = requests.post(endpoint, data=overpass_query)
    if response.ok:
        return _parse(response, **parse_kwargs)
    else:
        raise OverpassAPIError(response.text)


class OverpassAPIError(Exception):
    pass


class OverpassParseError(Exception):
    pass
