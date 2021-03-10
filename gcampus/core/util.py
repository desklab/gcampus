from typing import Tuple, Optional

from django.conf import settings
from geopy import Location
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim

"""Address Options

The address options are used for reverse geocoding. The response may
contain any of the fields in ``ADDRESS_OPTIONS`` but we only need one
field used for the ``location_name`` in
:class:`gcampus.core.models.Measurement`.
"""
ADDRESS_OPTIONS = ("city", "village", "municipality", "county", "state", "country")


def get_location_name(long_lat: Optional[Tuple[float, float]]) -> Optional[str]:
    """Get Location Name

    Get a name for the location specified as a parameter. Uses reverse
    geocoding to look up an address for the provided coordinates.

    :param long_lat: Tuple of longitude and latitude as float
    :returns: Optional string of location name
    """
    if long_lat is None:
        return None
    elif not isinstance(long_lat, tuple) or len(long_lat) != 2:
        raise ValueError("Tuple of longitude and latitude expected.")

    long, lat = long_lat
    geo_loc = get_geo_locator()
    try:
        loc: Optional[Location] = geo_loc.reverse((lat, long), exactly_one=True)
    except ValueError or GeocoderServiceError:
        return None
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
