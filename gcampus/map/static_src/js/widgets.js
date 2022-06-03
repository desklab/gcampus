/*
 * Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
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

import mapboxgl from '!mapbox-gl';

class MapboxGLPointWidget {
    TYPE = 'Point';
    _map;
    _marker;
    _markerAdded;
    _input;
    _value;  // GeoJSON object that will be stringified later

    constructor(map, input) {
        this._map = map;
        this._marker = new mapboxgl.Marker({draggable: true});
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
        this._map.fire('edit', {detail: {widget: this}});
    }

    _addMarker() {
        if (!this._markerAdded) {
            this._marker.addTo(this.getMap());
            this._markerAdded = true;
        }
    }

    _onMapClicked(e) {
        this.setLngLat(e.lngLat);
    }

    _onMarkerDragged(e) {
        this.setLngLat(e.target.getLngLat());
    }

    getLngLat() {
        let coordinates = this.value.coordinates;
        if (coordinates === null || coordinates.hasOwnProperty('lng'))
            return coordinates;
        return {
            lng: coordinates[0],
            lat: coordinates[1]
        };
    }

    setLngLat(lngLat) {
        if (lngLat !== null && lngLat.hasOwnProperty('lng')) {
            // lngLat is not an array but an object
            lngLat = [lngLat.lng, lngLat.lat];
        }
        this.value = {
            type: this.TYPE,
            coordinates: lngLat
        };
    }

    getMap() {
        return this._map;
    }

}

export {MapboxGLPointWidget};
