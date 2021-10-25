#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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

from typing import Tuple, Optional, Union

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.cache import cache
from geopy import Location
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim

from gcampus.core.apps import GCampusCoreAppConfig

"""Address Options

The address options are used for reverse geocoding. The response may
contain any of the fields in ``ADDRESS_OPTIONS`` but we only need one
field used for the ``location_name`` in
:class:`gcampus.core.models.Measurement`.
"""
ADDRESS_OPTIONS = ("city", "village", "municipality", "county", "state", "country")


def get_location_name(
    location: Union[Tuple[float, float], Point, None]
) -> Optional[str]:
    """Get Location Name (with caching)

    Get a name for the location specified as a parameter. Uses reverse
    geocoding to look up an address for the provided coordinates.

    :param location: Tuple of longitude and latitude as floats or Point
    :returns: Optional string of location name
    """
    if location is None:
        return None
    if isinstance(location, tuple):
        location = Point(location)
    elif not isinstance(location, Point) or len(location) != 2:
        raise ValueError("Tuple of longitude and latitude or Point expected.")

    location_tuple: Tuple[float, float] = rounded_location(location).tuple
    cache_key = __get_coords_cache_key(location_tuple)
    cached_result = cache.get(cache_key, default=None)
    if cached_result is not None:
        return cached_result
    # If this code is reached, the cache for the current location is
    # still empty and an API request has to be made
    try:
        result = __get_location_name(location_tuple)
    except (ValueError, GeocoderServiceError):
        # Skip trying to cache the result
        return None
    if result is not None:
        # Save the result of the geo lookup in cache
        # Timeout defaults to 100 days
        timeout = getattr(settings, "GEOLOCKUP_CACHE_TIMEOUT", 60 * 60 * 24 * 100)
        cache.set(cache_key, result, timeout)
    return result


def rounded_location(location: Point, precision: int = -2) -> Point:
    """Rounded Location

    Round the location to a provided precision (in metres).
    """
    if location.srid is None:
        location.srid = 4326  # default coordinate system
    if location.srid != 3857:
        location_rounded: Point = location.clone()
        # Transform location coordinates to metres
        location_rounded.transform(3857)
    else:
        # The provided location is already in the 3857 projection
        location_rounded: Point = location.clone()
    # At this point, location_rounded uses metre as a unit for x and y
    # (and z). Using round, the coordinates are rounded
    location_rounded.x = round(location_rounded.x, precision)
    location_rounded.y = round(location_rounded.y, precision)
    if location_rounded.hasz:
        location_rounded.z = round(location_rounded.z, precision)
    # Transform back to original projection
    location_rounded.transform(location.srid)
    return location_rounded


def __get_coords_cache_key(coords: Tuple[float, float]):
    long, lat = coords
    return f"{GCampusCoreAppConfig.label}:geolookup:cache:{long},{lat}"


def __get_location_name(location: Tuple[float, float]) -> Optional[str]:
    """Get Location Name

    Get a name for the location specified as a parameter. Uses reverse
    geocoding to look up an address for the provided coordinates.

    :param location: Tuple of longitude and latitude as floats
    :returns: Optional string of location name
    """
    long, lat = location
    geo_loc = get_geo_locator()
    loc: Optional[Location] = geo_loc.reverse((lat, long), exactly_one=True, timeout=5)
    if loc is not None and "address" in loc.raw:
        address = loc.raw["address"]
        for opt in ADDRESS_OPTIONS:
            if opt in address:
                return address[opt]
    return None


def get_geo_locator() -> Nominatim:
    return Nominatim(
        user_agent=getattr(settings, "NOMINATIM_USER_AGENT", "gcampus"),
        domain=getattr(settings, "NOMINATIM_DOMAIN", "nominatim.openstreetmap.org"),
    )
