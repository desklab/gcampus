from typing import Tuple, Optional

from django.conf import settings
from geopy import Location
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim

from gcampus.core.models import Measurement, StudentToken

from django.core.exceptions import PermissionDenied

from gcampus.core.models.token import TeacherToken

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
    except (ValueError, GeocoderServiceError):
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

def check_permission(request, token, measurement_id=None):
    """Check Permission

   This function checks if a by the user provided token is correct, thus checking if the user has
   the correct permissions to create/alter a measurement.

   First it is checked if the user is a superuser. If this is the case, True is returned, becuase a superuser
   has all permission.

   Then the length tells which token type was provided. If this token is valid and no measurement_id was provided,
   (a new measurement is being created) the acess is granted.

   If a measurement_id is provided, it is checked wether the token linked to the measurement matches the provided one.

    :param request: The request object. Contains e.g. the POST form
        data.
     :param token: Either a teacher or student token.
    :param measurement_id: This information comes from the URL and
        contains the ID to the measurement entry that is being
        edited.
    """

    if request.user.is_superuser:
        return True

    if len(token) == 8:
        token_type = "student"
        if not StudentToken.objects.filter(token=token).exists():
            raise PermissionDenied("Wrong Student Authentication Token")
    else:
        token_type = "teacher"
        if not TeacherToken.objects.filter(token=token).exists():
            raise PermissionDenied("Wrong Teacher Authentication Token")

    if measurement_id:
        measurement = Measurement.objects.get(pk=measurement_id)

        if not measurement:
            raise PermissionDenied("The measurement you want to alter does not exist")

        if token_type == "student":
            if not measurement.token == token:
                raise PermissionDenied("Wrong Student Authentication Token for requested Measurement")
        else:
            if not measurement.token.parent_token == token:
                raise PermissionDenied("Wrong Teacher Authentication Token for requested Measurement")

    return True
