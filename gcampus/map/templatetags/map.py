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
from typing import Tuple, Optional

from django import template
from django.conf import settings
from django.utils.http import urlencode

register = template.Library()


@register.inclusion_tag("gcampusmap/map.html")
def map(  # noqa
    name: str = "map",
    container: str = "map",
    center: Optional[Tuple[float, float]] = None,
    style: Optional[str] = None,
    zoom: Optional[float] = None,
    has_search: bool = True,
    mapbox_access_token: Optional[str] = None,
    onload: str = "",
    **kwargs,
):
    map_settings = getattr(settings, "MAP_SETTINGS")
    if center is None:
        center = map_settings["CENTER"]
    center_lng, center_lat = center
    if style is None:
        style = map_settings["STYLE"]
    if zoom is None:
        zoom = map_settings["ZOOM"]
    if mapbox_access_token is None:
        mapbox_access_token = map_settings["MAPBOX_ACCESS_TOKEN"]
    klass = kwargs.pop("class", "")
    return {
        "name": name,
        "container": container,
        "mapbox_access_token": mapbox_access_token,
        "mapbox_style": style,
        "zoom": zoom,
        "center_lng": center_lng,
        "center_lat": center_lat,
        "class": klass,
        "has_search": has_search,
        "onload": onload,
    }


@register.inclusion_tag("gcampusmap/loadjs.html")
def load_mapbox_js():
    return {}


@register.inclusion_tag("gcampusmap/loadcss.html")
def load_mapbox_css():
    return {}


@register.simple_tag()
def map_options_url(lng, lat, zoom) -> str:
    params = {"lng": lng, "lat": lat, "zoom": zoom}
    return f"?{urlencode(params)}"
