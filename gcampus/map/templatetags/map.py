from django import template

from gcampus.map.settings import MAP_SETTINGS

register = template.Library()


@register.inclusion_tag("gcampusmap/map.html")
def map(**kwargs):
    map_name = kwargs.pop("name", "map")
    map_container = kwargs.pop("container", "map")
    center_lat, center_lng = kwargs.pop("center", MAP_SETTINGS["CENTER"])
    style = kwargs.pop("style", MAP_SETTINGS["STYLE"])
    zoom = kwargs.pop("zoom", MAP_SETTINGS["ZOOM"])
    mapbox_access_token = MAP_SETTINGS["MAPBOX_ACCESS_TOKEN"]
    klass = kwargs.pop("class", "")
    onload = kwargs.pop("onload", "")
    return {
        "name": map_name,
        "container": map_container,
        "mapbox_access_token": mapbox_access_token,
        "mapbox_style": style,
        "zoom": zoom,
        "center_lng": center_lng,
        "center_lat": center_lat,
        "class": klass,
        "onload": onload,
    }


@register.inclusion_tag("gcampusmap/loadjs.html")
def load_mapbox_js():
    return {}


@register.inclusion_tag("gcampusmap/loadcss.html")
def load_mapbox_css():
    return {}
