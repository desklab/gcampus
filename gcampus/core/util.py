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

import datetime
import math
import time
from typing import List, Tuple, Optional, Union

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.utils import timezone
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
    lng, lat = location
    geo_loc = get_geo_locator()
    timeout = getattr(settings, "REQUEST_TIMEOUT", 5)
    loc: Optional[Location] = geo_loc.reverse(
        (lat, lng), exactly_one=True, timeout=timeout
    )
    if loc is not None and "address" in loc.raw:
        address = loc.raw["address"]
        for opt in ADDRESS_OPTIONS:
            if opt in address:
                return address[opt]
    return None


def get_geo_locator() -> Nominatim:
    return Nominatim(
        user_agent=getattr(settings, "REQUEST_USER_AGENT", "GewaesserCampus"),
        domain=getattr(settings, "NOMINATIM_DOMAIN", "nominatim.openstreetmap.org"),
    )


def get_intervals_from_today(date: datetime.datetime) -> List[datetime.datetime]:
    """Get intervals from today

    Returns a list of datetime objects that contain dates going back
    either from weeks, months or years, depending on the time interval
    from today to a given date.

    :param date: Datetime object to get the number of weeks
    :returns: List of datetime objects one interval (week, month or year) apart
    """
    today = timezone.now()
    num_bins = math.ceil((today - date).days / 7) + 2
    if not num_bins > 52:
        dates: List[datetime.datetime] = [
            today - datetime.timedelta(weeks=x) for x in reversed(range(num_bins))
        ]
        return dates

    num_bins = math.ceil((today - date).days / 30) + 2
    if not num_bins > 48:
        dates: List[datetime.datetime] = [
            today - datetime.timedelta(weeks=x * 4) for x in reversed(range(num_bins))
        ]
        return dates

    num_bins = math.ceil((today - date).days / 365) + 2
    dates: List[datetime.datetime] = [
        today - datetime.timedelta(weeks=x * 52) for x in reversed(range(num_bins))
    ]

    return dates


def get_measurement_intervals(
    interval_list: List[datetime.datetime], measurement_list: List[datetime.datetime]
) -> List[int]:
    """Get Measurements per bins

    Returns a list of percentages (ints) representing how many
    measurements were conducted in this time interval (weeks, months or years).

    :param interval_list: List of intervals to create numbers of measurements in
    :param measurement_list: List of measurements
    :returns: List of percentages representing how many measurements
        were conducted in this interval (week, month or year)
    """
    if not measurement_list:
        return []
    if len(interval_list) <= 1:
        return []
    measurements_per_interval = [0] * (len(interval_list) - 1)
    for measurement_date in measurement_list:
        for interval_index in range(len(interval_list) - 1):
            if (
                interval_list[interval_index]
                <= measurement_date
                <= interval_list[interval_index + 1]
            ):
                measurements_per_interval[interval_index] += 1
                break
    max_measurements = max(measurements_per_interval)
    return list(
        map(lambda m: int(m / max_measurements * 100), measurements_per_interval)
    )


def convert_dates_to_js_milliseconds(dates: List[datetime.datetime]) -> List[int]:
    """Get Dates for javascript

    Since Javascript doesn't know python datetime objects we need to
    convert these into milliseconds.

    :param dates: List of dates
    :returns: List of dates as milliseconds
    """
    dates_milliseconds: List[int] = [
        int(time.mktime(date.timetuple())) * 1000 for date in dates
    ]
    return dates_milliseconds
