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

import datetime
import time
import math
from typing import List, Tuple, Optional, Union, Set

import numpy as np
from django.utils import timezone
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.cache import cache
from geopy import Location
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim

from gcampus.core.apps import GCampusCoreAppConfig
from gcampus.core.models.util import EMPTY

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


def get_weeks_from_today(date: datetime.datetime) -> List[datetime.datetime]:
    """Get Weeks from today

    Returns a list of datetime objects that contain dates going back
    weekly from today to a given date.

    :param date: Datetime object to get the number of weeks
    :returns: List of datetime objects one week apart
    """
    today = timezone.now()
    num_weeks = math.ceil((today - date).days / 7) + 1
    dates: List[datetime.datetime] = [
        today - datetime.timedelta(weeks=x) for x in reversed(range(num_weeks))
    ]
    return dates


def get_measurements_per_week(
    week_list: List[datetime.datetime], measurement_list: List[datetime.datetime]
) -> List[int]:
    """Get Measurements per weeks

    Returns a list of percentages (ints) representing how many measurements were conducted in this week

    :param week_list: List of weeks to create numbers of measurements in
    :param measurement_list: List of measurements
    :returns: List of percentages representing how many measurements were conducted in this week
    """
    if not measurement_list:
        return []
    measurements_per_week = [0] * (len(week_list) - 1)

    for measurement_date in measurement_list:
        for week_index in range(len(week_list) - 1):
            if week_list[week_index] <= measurement_date <= week_list[week_index + 1]:
                measurements_per_week[week_index] += 1
                break
    measurements_per_week = (
        np.array(measurements_per_week) / np.max(measurements_per_week) * 100
    )
    return [int(measurement_val) for measurement_val in measurements_per_week]


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


def get_all_filters(old_filters: Set[str], new_filters: List[str]) -> List[str]:
    """Get Number of Filters

    This function takes a list of old filters and a list of new filters and returns a list of the
    all applied filters.

    :param old_filters: List of old applied filters
    :param new_filters: List of new applied filters
    :returns: List of new applied filters
    """
    all_filters = set(old_filters)
    for filter_item in new_filters:
        all_filters.add(filter_item)
    # For some reason every time the filter button is pressed the location filter is set. Since the location filter
    # needs some further improvement I'll fix it like this
    # TODO fix location filter and remove this
    if "location" in all_filters:
        all_filters.remove("location")

    return list(all_filters)


def get_filter_status(new_filters: List[str]) -> bool:
    """Get Filter Status

    This function takes a list of new filters and returns a bool corresponding
    to the status of the filter

    :param new_filters: List of new applied filters
    :returns: Bool if filter is set
    """
    if "name" in new_filters:
        new_filters.remove("name")
    if new_filters in EMPTY:
        return False
    return True
