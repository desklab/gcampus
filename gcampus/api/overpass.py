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

    def get_element_type(self) -> str:
        raise NotImplementedError()

    def get_name(self) -> str:
        # Use german name by default
        name: str = self.tags.get("name:de", "")
        if name == "":
            # Fall back to international name
            name = self.tags.get("name", "")
        return name


@dataclass
class Node(Element):
    def get_element_type(self) -> str:
        return "node"


@dataclass
class Way(Element):
    def get_element_type(self) -> str:
        return "way"


@dataclass
class Relation(Element):
    def get_element_type(self) -> str:
        return "relation"


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
        unclosed_inner: List[LineString] = []
        # List of outer rings (e.g. for a lake this would be the
        # shoreline)
        outer: List[LinearRing] = []
        unclosed_outer: List[LineString] = []
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
            geos_line_string = LineString(line_string)
            role = member.get("role")
            if role == "inner":
                if geos_line_string.closed:
                    inner.append(LinearRing(line_string))
                else:
                    unclosed_outer.append(geos_line_string)
            elif role == "outer":
                if geos_line_string.closed:
                    outer.append(LinearRing(line_string))
                else:
                    unclosed_outer.append(geos_line_string)
            else:
                other.append(geos_line_string)

        unclosed_outer, _outer = merge_unclosed_lines(unclosed_outer)
        unclosed_inner, _inner = merge_unclosed_lines(unclosed_inner)
        outer += _outer
        inner += _inner
        other += unclosed_outer
        other += unclosed_inner

        if len(outer) > 0:
            # Construct polygons for each outer ring and subtract all
            # inner rings. Merge all polygons into a multi polygon
            if len(outer) == 1:
                polygons = Polygon(outer[0], inner)
            else:
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


def merge_unclosed_lines(
    unclosed_lines: List[LineString],
) -> Tuple[List[LineString], List[LinearRing]]:
    _union = union(unclosed_lines)
    if _union is None:
        return [], []
    elif isinstance(_union, (LineString, MultiLineString)):
        _union = _union.merged
    else:
        raise TypeError(f"Unhandled type '{type(_union)}' for line union.")

    if isinstance(_union, LineString):
        if _union.closed:
            return [], [ring_from_string(_union)]
        else:
            return [_union], []
    elif isinstance(_union, MultiLineString):
        rings: List[LinearRing] = []
        lines: List[LineString] = []
        line: LineString
        for line in _union:
            if line.closed:
                rings.append(ring_from_string(line))
            else:
                lines.append(line)
        return lines, rings


def ring_from_string(line_string: LineString) -> LinearRing:
    if not line_string.closed:
        raise ValueError("LineString is not closed!")
    return LinearRing(line_string.tuple)


def union(geometries: List[GEOSGeometry]) -> Optional[GEOSGeometry]:
    if len(geometries) < 1:
        return None
    _geos_union = geometries[0]
    for geometry in geometries[1:]:
        _geos_union = _geos_union.union(geometry)
    return _geos_union


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
    user_agent = getattr(
        settings, "OVERPASS_USERAGENT", f"GewaesserCampus ({settings.GCAMPUS_HOMEPAGE})"
    )
    response: requests.Response = requests.post(
        endpoint,
        data=overpass_query.encode("utf-8"),
        headers={"User-Agent": user_agent},
    )
    if response.ok:
        return _parse(response, **parse_kwargs)
    else:
        raise OverpassAPIError(response.text)


class OverpassAPIError(Exception):
    pass


class OverpassParseError(Exception):
    pass
