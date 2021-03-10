{% extends "gis/admin/openlayers.js" %}
{% block map_creation %}
{{ module }}.map = new OpenLayers.Map('{{ id }}_map', options);
// Base Layer
{{ module }}.layers.base = new OpenLayers.Layer.OSM("OpenStreetMap (Mapnik)");
{{ module }}.layers.base.tileOptions.crossOriginKeyword = null;
{{ module }}.layers.base.tileOptions.crossOrigin = null;
{{ module }}.map.displayProjection = new OpenLayers.Projection("EPSG:4326");
{{ module }}.map.addLayer({{ module }}.layers.base);
{% endblock %}
