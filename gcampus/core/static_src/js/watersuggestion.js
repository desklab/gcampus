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

const DEFAULT_COLOR = '#052c65';
const HIGHLIGHT_COLOR = '#0d6efd';
const waterSuggestionTemplate = (
    document.getElementById('waterSuggestionTemplate').text
);
const parentElement = document.getElementById('waterSuggestions');
const loadingElement = document.getElementById('waterLoading');
const osmElement = document.getElementById('waterOsm');
const customWaterElement = document.getElementById('waterCustom');
const EMPTY_GEO_JSON = {
    'type': 'FeatureCollection',
    'features': []  // Empty data for now
};


class UnknownSourceError extends Error {
    constructor(message) {
        super(message);
        this.message = (
            'Unknown source \'' + message + '\'. Can be either \'osm\' or \'db\'.'
        );
        this.name = 'UnknownSourceError';
    }
}


/**
 * Construct water lookup query
 *
 * This method prepares a request to the gcampus API using either the
 * database or OpenStreetMaps as a source.
 *
 * @param source {string} - Can be either 'osm' or 'db'
 * @param lng {number|string} - Longitude
 * @param lat {number|string} - Latitude
 * @returns {string} - URL for the query
 */
function getLookupQuery(source, lng, lat) {
    let url;
    if (source === 'osm') {
        url = '/api/v1/overpasslookup/';
    } else if (source === 'db') {
        url = '/api/v1/waterlookup';
    } else {
        throw UnknownSourceError(String(source));
    }
    // Parse string inputs for rounding later
    if (typeof lat !== 'number')
        lat = Number.parseFloat(lat);
    if (typeof lng !== 'number')
        lng = Number.parseFloat(lng);
    // Round the location to 3 digits. This should be precise enough.
    let location = `POINT (${lng.toFixed(5)} ${lat.toFixed(5)})`;
    let bboxSize = '800';  // 800 meter square bounding box
    let params = {
        geo_center: location,
        geo_size: bboxSize
    };
    let searchParams = new URLSearchParams(params).toString();
    return [url, searchParams].join('?');
}


/**
 * Fetch Water Lookup (database)
 *
 * This method sends a request to the gcampus API to find nearby points
 * of interest with the tag "natural=water".
 *
 * @param lng {number|string} - Longitude
 * @param lat {number|string} - Latitude
 * @returns {Promise} - Fetch promise
 */
function fetchWaterLookup(lng, lat) {
    let lookupQuery = getLookupQuery('db', lng, lat);
    return fetch(lookupQuery).then(response => response.json());
}


/**
 * Fetch Overpass Lookup (OpenStreetMaps)
 *
 * This method sends a request to the gcampus API to find nearby points
 * of interest with the tag "natural=water".
 *
 * @param lng {number|string} - Longitude
 * @param lat {number|string} - Latitude
 * @returns {Promise} - Fetch promise
 */
function fetchOverpassLookup(lng, lat) {
    let lookupQuery = getLookupQuery('osm', lng, lat);
    return fetch(lookupQuery).then(response => response.json());
}


/**
 * Water List Item
 *
 * Returns an element used to display a list of water suggestions inside
 * the ``WaterList`` class.
 *
 * @param feature
 * @returns {NodeList}
 */
function ListItem(feature) {
    let {display_name, display_flow_type, flow_type} = feature.properties;
    let id = feature.id;
    let inputId = 'waterSuggestion' + String(id);
    let item = document.createElement('div');
    item.innerHTML = waterSuggestionTemplate;
    let input = item.querySelector('input');
    let label = item.querySelector('label');
    let nameElement = item.querySelector('label > b');
    let descriptionElement = item.querySelector('label > small');
    input.setAttribute('id', inputId);
    input.setAttribute('data-feature-id', id);
    label.setAttribute('for', inputId);
    label.setAttribute('data-feature-id', id);
    nameElement.innerText = display_name;
    descriptionElement.innerText = (
        display_flow_type.charAt(0).toUpperCase() + display_flow_type.slice(1)
    );
    if (flow_type === 'standing' || flow_type === 'running') {
        let icon = document.createElement('i');
        icon.classList.add('water-icon');
        icon.classList.add('me-1');
        icon.classList.add(flow_type);
        descriptionElement.insertAdjacentElement('afterbegin', icon);
    }
    return item.childNodes;
}


/**
 * Append nodes to HTMLElement
 *
 * Append nodes (NodeList) in-place.
 *
 * @param parent {HTMLElement} - Parent element
 * @param children {NodeList} - List of nodes
 */
function insertNodes(parent, children) {
    let pos = parent.firstChild;
    while (children.length > 0) {
        parent.insertBefore(children[0], pos);
    }
}


class WaterList {
    state;
    map;
    currentPermanentHighlight;
    currentHighlight;
    _layerID = 'waterLayer';
    _layerIDPoint = 'waterLayerPoint';
    _sourceID = 'waterList';
    _requestTimeout = null;
    lat = null;
    lng = null;

    constructor() {
        this.state = {
            features: [],
            hasDatabase: false,
            hasOsm: false,
            loading: false,
            error: false
        };
        this.currentPermanentHighlight = null;
        this.currentHighlight = null;
        window.addEventListener('map:load', this.mapLoad.bind(this));
        osmElement.addEventListener('click', this.osmUpdate.bind(this));
    }

    setState(state) {
        let keys = Object.keys(this.state);
        for (let i = 0; i < keys.length; i++) {
            let key = keys[i];
            if (Object.prototype.hasOwnProperty.call(state, key))
                this.state[key] = state[key];
        }
        this.render();
    }

    setFeatures(features, source) {
        if (source === 'osm') {
            features = this.state.features.concat(features || []);
        } else if (source === 'db') {
            features = features || [];
        } else {
            throw UnknownSourceError(String(source));
        }

        // Add all features to the layer
        this.map.getSource(this._sourceID).setData({
            'type': 'FeatureCollection',
            'features': features
        });
        this.map.removeFeatureState({source: this._sourceID});

        if (this.currentPermanentHighlight !== null) {
            let hlFeature = features.filter(
                (f) => f.id === this.currentPermanentHighlight
            );
            if (hlFeature.length !== 1) {
                this.currentPermanentHighlight = null;
            }
        }
        this.highlightFeature(this.currentPermanentHighlight);

        if (source === 'osm') {
            this.setState({
                loading: false,
                features: features,
                hasOsm: true,
            });
        } else {
            this.setState({
                loading: false,
                features: features,
                hasDatabase: true
            });
        }
    }

    /**
     * Highlight Feature
     *
     * Highlight a feature layer by a given ID. This will change the
     * color of the layer to visually distinguish one layer from the
     * others.
     *
     * @param featureId {number}: Feature ID
     */
    highlightFeature(featureId) {
        if (this.currentHighlight === featureId) {
            return;
        }
        this.map.removeFeatureState({
            source: this._sourceID,
            id: this.currentHighlight
        });
        this.currentHighlight = featureId;
        if (this.currentHighlight === null) {
            return;
        }
        this.map.setFeatureState({
            source: this._sourceID,
            id: this.currentHighlight
        }, {
            highlight: true
        });
    }

    highlightPermanent(featureId) {
        this.currentPermanentHighlight = featureId;
        this.highlightFeature(this.currentPermanentHighlight);
    }

    clearLayers() {
        this.map.getSource(this._sourceID).setData(EMPTY_GEO_JSON);
    }

    /**
     * Update Map
     *
     * Called when the map is being edited (i.e. a marker is placed).
     * Makes a request to the gcampus API which then requests the
     * overpass API to find all waters in proximity to the marker.
     *
     * @param e {Event}: Event, passed by the event listener
     */
    mapUpdate(e) {
        let pointWidget = e.detail.widget;
        let {lng, lat} = pointWidget.getLngLat();
        this.lat = lat;
        this.lng = lng;

        this.setState({
            loading: true,
            hasDatabase: false,
            hasOsm: false,
            features: [],
        });
        this.clearLayers();
        this.currentHighlight = null;

        if (this._requestTimeout !== null) {
            // Stop the last timeout and thereby abort the request
            clearTimeout(this._requestTimeout);
        }
        // Start a timeout and wait for 300ms. After this timeout, do
        // the actual request. This delay is acceptable as the Overpass
        // API request is quite lengthy and thus another 300ms will not
        // matter.
        // This is done to avoid spamming requests when the user double
        // clicks on the map e.g. to zoom. Only the last click will go
        // through to the server.
        this._requestTimeout = setTimeout(() => {
            this._requestTimeout = null;
            fetchWaterLookup(lng, lat)
                .then(data => this.setFeatures(data.features, 'db'))
                .catch(this.onError.bind(this));
        }, 300);
    }

    osmUpdate() {
        if (this.lat === null || this.lng === null) {
            return;
        }
        this.setState({
            loading: true
        });
        fetchOverpassLookup(this.lng, this.lat)
            .then(data => this.setFeatures(data.features, 'osm'))
            .catch(this.onError.bind(this));
    }

    onError(err) {
        this.setState({
            loading: false,
            error: true,
        });
        console.error(err);
    }

    /**
     * Initialize Map
     *
     * Saves the map and GeoJSON layer and registers the event listner
     * for updating markers.
     *
     * @param e {Event}: Passed by the event listener for map
     *      initialisation.
     */
    mapLoad(e) {
        this.map = e.detail.map;
        this.map.addSource(this._sourceID, {
            'type': 'geojson',
            'data': EMPTY_GEO_JSON,
        });
        // Add the default water layer. This layer will show all waters
        // suggested to the user. It automatically updates once the
        // source data is changed. There is thus no need to access this
        // layer later on.
        this.map.addLayer({
            'id': this._layerID,
            'type': 'line',
            'source': this._sourceID,
            'layout': {},
            'paint': {
                'line-color': [
                    'case',
                    ['boolean', ['feature-state', 'highlight'], false],
                    HIGHLIGHT_COLOR,
                    DEFAULT_COLOR,
                ],
                'line-width': [
                    'case',
                    ['boolean', ['feature-state', 'highlight'], false],
                    5,
                    4,
                ]
            },
            'filter': ['!=', '$type', 'Point']
        });
        this.map.addLayer({
            'id': this._layerIDPoint,
            'type': 'circle',
            'source': this._sourceID,
            'paint': {
                'circle-color': [
                    'case',
                    ['boolean', ['feature-state', 'highlight'], false],
                    HIGHLIGHT_COLOR,
                    DEFAULT_COLOR,
                ],
                'circle-radius': [
                    'case',
                    ['boolean', ['feature-state', 'highlight'], false],
                    10,
                    8,
                ],
                'circle-stroke-width': [
                    'case',
                    ['boolean', ['feature-state', 'highlight'], false],
                    3,
                    2,
                ],
                'circle-stroke-color': '#ffffff'
            },
            'filter': ['==', '$type', 'Point']
        });
        // Add highlight layer. This will automatically update once the
        // highlighted data source is set.
        this.map.on('edit', this.mapUpdate.bind(this));
    }

    render() {
        let {features, loading, hasDatabase, hasOsm} = this.state;
        parentElement.querySelectorAll('input,label').forEach(
            (el) => parentElement.removeChild(el)
        );
        for (let i = 0; i < features.length; i++) {
            let feature = features[i];
            insertNodes(parentElement, ListItem(feature));
            let input = parentElement.querySelector(
                'input[data-feature-id="' + String(feature.id) + '"]'
            );
            let label = parentElement.querySelector(
                'label[data-feature-id="' + String(feature.id) + '"]'
            );
            input.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.highlightPermanent(feature.id);
                }
            });
            label.addEventListener('mouseenter', () => {
                this.highlightFeature(feature.id);
            });
            label.addEventListener('mouseleave', () => {
                this.highlightFeature(this.currentPermanentHighlight);
            });
            if (this.currentPermanentHighlight === feature.id) {
                input.checked = true;
            }
        }
        if (loading) {
            loadingElement.classList.remove('d-none');
            osmElement.classList.add('d-none');
            customWaterElement.classList.add('d-none');
        } else {
            loadingElement.classList.add('d-none');
            if (hasDatabase) {
                if (hasOsm) {
                    osmElement.classList.add('d-none');
                    customWaterElement.classList.remove('d-none');
                } else {
                    osmElement.classList.remove('d-none');
                    customWaterElement.classList.add('d-none');
                }
            } else {
                osmElement.classList.add('d-none');
                customWaterElement.classList.add('d-none');
            }
        }
    }
}

new WaterList();
