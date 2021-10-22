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

import {GeoSearchControl, OpenStreetMapProvider} from 'leaflet-geosearch';
import 'leaflet-geosearch/assets/css/leaflet.css';

const search = new GeoSearchControl({
    style: 'bar',
    showMarker: false,
    showPopup: false,
    autoCompleteDelay: 400,  // Default is 250
    maxSuggestions: 5,
    provider: new OpenStreetMapProvider(),
});

window.addEventListener('map:init', function (e) {
    let target_map = e.detail.map;
    target_map.addControl(search);
});
