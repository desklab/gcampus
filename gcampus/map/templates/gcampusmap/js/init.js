{% load l10n %}
'use strict';

let mapboxgl = gcampus.mapboxgl;

mapboxgl.accessToken = '{{ mapbox_access_token }}'
const map = new mapboxgl.Map({
    container: '{{ container }}',
    style: '{{ mapbox_style }}',
    center: [{{ center_lng|unlocalize }}, {{ center_lat }}],
    zoom: {{ zoom }},
    attributionControl: false
});
map.addControl(
    new mapboxgl.AttributionControl({ compact: true})
);
var nav = new mapboxgl.NavigationControl();
map.addControl(nav, 'top-left');

{% if onload %}
map.on('load', {{ onload }});
{% endif %}

if (window._maps === undefined) {
    window._maps = {};
}
window._maps['{{ name }}'] = map;
