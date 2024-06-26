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

import logging
from hashlib import md5
from typing import Tuple, Optional, List
from urllib.parse import quote, urljoin

import httpx
from django.conf import settings
from django.contrib.gis.geos import Point, MultiPoint
from django.core.cache import cache
from django.urls import reverse

from gcampus.core import get_base_url
from gcampus.map.clustering import mean_shift_clustering

logger = logging.getLogger("gcampus.map.static")


def _create_pin(
    point: Point, size: str = "l", color: str = "2760A4", label: str = ""
) -> str:
    """Construct a pin string according to the Mapbox Static Images
    API schema.

    :param point: The point (i.e. coordinates) of the marker/pin. Has to
        be of type :class:`django.contrib.gis.geos.Point`.
    :param size: Either 'l' or 's'. Sets the size of the marker.
    :param color: 3- or 6-character hex color code.
    :param label: Optional label. Leave blank (``""``) for no label.
    :returns: An overlay pin string.
    """
    if label != "":
        label = f"-{label}"
    return f"pin-{size}{label}+{color}({point.x},{point.y})"


def _create_cluster_marker(point: Point, count: int) -> str:
    """Construct a pin string according to the Mapbox Static Images
    API schema for clustered custom markers.

    :param point: The point (i.e. coordinates) of the marker/pin. Has to
        be of type :class:`django.contrib.gis.geos.Point`.
    :param count: Number of measurements at that location.
    :returns: An overlay marker string.
    """
    if settings.DEBUG:
        # In debug mode, the generated url will be from host 'localhost'
        # and thus not be accessible for Mapbox. Use Mapbox markers
        # instead.
        if count > 99:
            count = 99
            return _create_pin(point, label=str(count))
    url = reverse(
        "gcampusmap:marker",
        kwargs={"count": count, "version": settings.GCAMPUS_VERSION},
    )
    full_url = urljoin(get_base_url(), url)
    url_quote = quote(full_url, safe="")
    return f"url-{url_quote}({point.x},{point.y})"


def _get_cache_key(url: str) -> str:
    """Generate a cache key for static map images. To simplify and
    declutter the key, a md5 hash is used. Note that security is not
    crucial here, as the key is only used for cache lookups.
    """
    hasher = md5(url.encode(), usedforsecurity=False)
    return f"gcampus_cache_static_map_{hasher.hexdigest()!s}"


def get_static_map(
    markers: List[Point] | MultiPoint,
    center: Optional[Tuple[float, float]] = None,  # Order: lng, lat
    zoom: Optional[float] = 15,
    bbox: Optional[Tuple[float, float, float, float]] = None,
    size: Tuple[int, int] = (800, 600),
    padding: Optional[int] = 50,
    max_markers: int | None = None,
    pin_size: str = "l",
    attribution: bool = False,  # Important: Add attribution elsewhere
    access_token: Optional[str] = None,
    style_id: Optional[str] = None,
    client: Optional[httpx.Client] = None,
    timeout: Optional[int] = None,
) -> tuple[bytes, bool]:
    """Get a static map image from the Mapbox API.

    :param markers: List of points.
    :param center: Optional center coordinates (longitude, latitude).
    :param zoom: Required if ``center`` is specified. Defaults to 15.
    :param bbox: Optional bounding box tuple for the map. If both
        ``bbox`` and ``center`` are provided, the ``center`` argument
        is ignored.
    :param size: Image size (in pixels).
    :param padding: Optional padding. Ignored if ``bbox`` is ``None``
        but ``center`` is specified.
    :param max_markers: Maximum number of markers allowed. If the passed
        number of markers exceeds this, the markers are clustered
        instead. If ``None``, the default number is chosen from the
        settings (``MAX_MARKER_PRINT`` in ``MAP_SETTINGS``)
    :param pin_size: Size of the pins/markers as specified in
        ``markers``.
    :param attribution: If set to ``False``, the OpenStreetMap
        attribution is hidden from the image. Note that the attribution
        has to be placed elsewhere in that case.
    :param access_token: Optional Mapbox access token. Defaults to the
        backend access token specified in the settings.
    :param style_id: Optional Mapbox style ID. Defaults to the style ID
        as specified in the settings.
    :param client: Optional HTTPX client.
    :param timeout: Optional timeout, defaults to the default timeout
        (``REQUEST_TIMEOUT``).
    :returns: ``(image, clustered)``: Tuple of an image as bytes and
        a boolean indicating whether the points are clustered.
    """
    if bbox is None and center is None:
        positioning = "auto"
    elif bbox is not None:
        positioning = f"[{','.join(map(str, bbox))}]"
    else:
        # Position based on the 'center' argument
        if zoom is None:
            raise ValueError("'zoom' is required when using 'center'")
        positioning = f"{center[0]:f},{center[1]:f},{zoom}"

    mapbox_settings: dict = getattr(settings, "MAP_SETTINGS")
    if access_token is None:
        access_token = mapbox_settings["MAPBOX_BACKEND_ACCESS_TOKEN"]
    if style_id is None:
        style_id = mapbox_settings["STYLE_ID_PRINT"]
    if timeout is None:
        timeout = getattr(settings, "REQUEST_TIMEOUT", 5)
    if max_markers is None:
        max_markers = mapbox_settings["MAX_MARKER_PRINT"]
    clustered: bool = len(markers) > max_markers
    if clustered:
        markers, counts = mean_shift_clustering(markers)
        overlay = ",".join(
            _create_cluster_marker(p, count) for p, count in zip(markers, counts)
        )
    else:
        overlay = ",".join(_create_pin(p, size=pin_size) for p in markers)
    url = (
        f"https://api.mapbox.com/styles/v1/{style_id}"
        f"/static/{overlay}/{positioning}/{size[0]}x{size[1]}@2x"
    )
    sentinel = object()  # Like None, but not actually None
    cache_key = _get_cache_key(url)
    cached_val = cache.get(cache_key, sentinel)
    if cached_val is not sentinel:
        logger.debug("Found cached static map")
        return cached_val, clustered
    logger.debug("Map not cached, requesting new map instead")
    params = {"access_token": access_token}
    if not attribution:
        params["attribution"] = "false"
    if padding is not None and (bbox is not None or positioning == "auto"):
        params["padding"] = padding
    user_agent = getattr(
        settings, "REQUEST_USER_AGENT", f"GewaesserCampus ({settings.GCAMPUS_HOMEPAGE})"
    )
    if client is None:
        _client = httpx.Client()
    else:
        _client = client
    try:
        logger.debug("Requesting map from Mapbox...")
        response: httpx.Response = _client.get(
            url,
            params=params,
            headers={"User-Agent": user_agent},
            timeout=timeout,
        )
    except httpx.TimeoutException as e:
        raise TimeoutError from e
    finally:
        if client is None:
            # Close '_client' manually. Otherwise, the client has to be
            # closed by the caller of this function.
            _client.close()
    response.raise_for_status()
    if response.is_success:
        content = response.content
        logger.debug("Caching static map for later use...")
        cache.set(cache_key, content)
        return content, clustered
    # Unreachable code. If the response is not successful, an exception
    # will be raised in a previous step.
