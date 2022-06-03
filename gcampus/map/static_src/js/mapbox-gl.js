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
import MapboxGeocoder from '@mapbox/mapbox-gl-geocoder';
import {MapboxGLPointWidget} from './widgets';
import {setupCluster} from './clustering';

import '../styles/map.scss';

/**
 *
 * @param accessToken {string}
 * @param name {string}
 * @param container {string}
 * @param style {string}
 * @param defaultCenter {[number, number]}
 * @param defaultZoom {number}
 * @param hasSearch {boolean}
 * @param onload
 * @returns {mapboxgl.Map}
 */
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
    let map = new mapboxgl.Map({
        accessToken: accessToken,
        container: container,
        style: style,
        center: center,
        zoom: zoom,
        logoPosition: 'bottom-left',
        // Completely disable map pitch (tilt)
        pitchWithRotate: true,
        pitch: 0,
        maxPitch: 0,
        minPitch: 0
    });
    let nav = new mapboxgl.NavigationControl();
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
        if (onload !== null) {
            onload(e);
        }
    });
    if (window._maps === undefined) {
        window._maps = {};
    }
    window._maps[name] = map;
    return map;
}

/**
 *
 * @param center {[number, number]}
 * @param zoom {number}
 * @returns {{center: [number, number], zoom: number}}
 */
function getMapCenterZoom(center, zoom) {
    let urlString = window.location.href;
    if (urlString.includes('?')) {
        let paramString = urlString.split('?')[1];
        let queryString = new URLSearchParams(paramString);
        let params = Object.fromEntries(queryString.entries());
        if (params.hasOwnProperty('lng') && params.hasOwnProperty('lat'))
            center = [
                Number.parseFloat(params['lng']),
                Number.parseFloat(params['lat'])
            ];
        if (params.hasOwnProperty('zoom'))
            zoom = Number.parseFloat(params['zoom']);
    }
    return {center: center, zoom: zoom};
}


export {initMap, MapboxGLPointWidget, mapboxgl, setupCluster};
