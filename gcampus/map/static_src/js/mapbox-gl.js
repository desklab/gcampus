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

import mapboxgl from 'mapbox-gl'; // noqa
import 'mapbox-gl/dist/mapbox-gl.css';

class MapboxGLPointWidget {
    _map: mapboxgl.Map;
    _marker: mapboxgl.Marker;
    _markerAdded: Boolean;
    _input: HTMLElement;
    _value: Object;  // GeoJSON object that will be stringified later

    constructor(map: mapboxgl.Map, input: HTMLElement) {
        this._map = map;
        this._marker = new mapboxgl.Marker({draggable: true});
        this._markerAdded = false;
        this._input = input;

        // Set initial value using default value
        this._value = {
            type: 'Point',
            coordinates: null
        };
        if (this._input.value !== '') {
            // Overwrite default value using the value of the textfield
            this._value = JSON.parse(this._input.value);
        }

        // Register click listener for map
        this._map.on('click', this._onMapClicked.bind(this));
        // Register drag end listener for marker
        this._marker.on('dragend', this._onMarkerDragged.bind(this));
    }

    _onMapClicked(e) {
        this._marker.setLngLat(e.lngLat);
        this._updateLocation(e.lngLat);
        if (!this._markerAdded) {
            this._marker.addTo(this._map);
            this._markerAdded = true;
        }
    }

    _onMarkerDragged() {
        this._updateLocation(this.getLngLat());
    }

    _updateLocation(lngLat) {
        this._value.coordinates = [lngLat.lng, lngLat.lat];
        this._input.value = JSON.stringify(this._value);
        this._map.fire('edit', {detail: {widget: this}});
    }

    getLngLat() {
        return this._marker.getLngLat();
    }

    getMap() {
        return this._map;
    }

}

export {mapboxgl, MapboxGLPointWidget};
