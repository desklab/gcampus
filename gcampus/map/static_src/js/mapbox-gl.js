/*
 * Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import {Map, Marker, NavigationControl} from 'mapbox-gl'; // noqa
import MapboxGeocoder from '@mapbox/mapbox-gl-geocoder';

import '../styles/map.scss';

class MapboxGLPointWidget {
    TYPE = 'Point';
    _map;
    _marker;
    _markerAdded;
    _input;
    _value;  // GeoJSON object that will be stringified later

    constructor(map, input) {
        this._map = map;
        this._marker = new Marker({draggable: true});
        this._markerAdded = false;
        this._input = input;

        if (this._input.value !== '') {
            // Overwrite default value using the value of the textfield
            this.value = JSON.parse(this._input.value);
            this.getMap().flyTo({
                center: this.getLngLat(),
                zoom: 14,
                bearing: 0,
            });
        } else {
            // Set initial value using default value
            this.setLngLat(null);
        }

        // Register click listener for map
        this._map.on('click', this._onMapClicked.bind(this));
        // Register drag end listener for marker
        this._marker.on('dragend', this._onMarkerDragged.bind(this));
    }

    get value() {
        return this._value;
    }

    set value(val) {
        if (!val.hasOwnProperty('coordinates')) {
            throw Error('New value has no property `coordinates`');
        }
        this._value = val;
        let lngLat = this.getLngLat();
        if (lngLat !== null) {
            if (this._marker.getLngLat() !== lngLat) {
                // Only update the coordinates if they differ. Important
                // when marker is dragged.
                this._marker.setLngLat(lngLat);
            }
            // Make sure the marker is added to the map
            this._addMarker();
            // Set the value of the input element used for the form.
            this._input.value = JSON.stringify(val);
        }
    }

    _addMarker() {
        if (!this._markerAdded) {
            this._marker.addTo(this.getMap());
            this._markerAdded = true;
        }
    }

    _onMapClicked(e) {
        this.setLngLat(e.lngLat);
        this._map.fire('edit', {detail: {widget: this}});
    }

    _onMarkerDragged() {
        this.setLngLat(e.lngLat);
        this._map.fire('edit', {detail: {widget: this}});
    }

    getLngLat() {
        let coordinates = this.value.coordinates;
        if (coordinates === null || coordinates.hasOwnProperty('lng'))
            return coordinates;
        return {
            lng: coordinates[0],
            lat: coordinates[1]
        }
    }

    setLngLat(lngLat) {
        if (lngLat !== null && lngLat.hasOwnProperty('lng')) {
            // lngLat is not an array but an object
            lngLat = [lngLat.lng, lngLat.lat];
        }
        this.value = {
            type: this.TYPE,
            coordinates: lngLat
        }
    }

    getMap() {
        return this._map;
    }

}

function initMap(
    accessToken,
    name,
    container,
    style,
    defaultCenter,
    defaultZoom,
    hasSearch,
    onload,
) {
    let {center, zoom} = getMapCenterZoom(defaultCenter, defaultZoom);
    let map = new Map({
        accessToken: accessToken,
        container: container,
        style: style,
        center: center,
        zoom: zoom,
        logoPosition: 'bottom-left'
    });
    let nav = new NavigationControl();
    map.addControl(nav, 'top-left');
    if (hasSearch) {
        map.addControl(
            new MapboxGeocoder({
                accessToken: accessToken,
                marker: false,
            }),
            'top-right'
        );
    }
    if (onload !== null) {
        map.on('load', onload);
    }
    map.on('load', function (e) {
        // The target of the event will be set by dispatch event and can
        // thus not be used.
        // Instead, the 'detail' attribute will be used to hold the map.
        let event = new CustomEvent('map:load', {
            detail: {
                map: e.target
            }
        });
        // Here, the target will be set to 'window'
        window.dispatchEvent(event);
    });
    if (window._maps === undefined) {
        window._maps = {};
    }
    window._maps[name] = map;
    return map
}

function getMapCenterZoom(center, zoom) {
    let urlString = window.location.href;
    if (urlString.includes('?')) {
        let paramString = urlString.split('?')[1];
        let queryString = new URLSearchParams(paramString);
        let params = Object.fromEntries(queryString.entries());
        if (params.hasOwnProperty('lng') && params.hasOwnProperty('lat'))
            center = [params['lng'], params['lat']];
        if (params.hasOwnProperty('zoom'))
            zoom = params['zoom'];
    }
    return {center: center, zoom: zoom};
}


export {initMap, MapboxGLPointWidget};
