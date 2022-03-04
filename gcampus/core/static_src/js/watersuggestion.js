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

//import mapboxgl from 'mapbox-gl'; // noqa
import {Component, render} from 'preact';
import {html} from 'htm/preact';


const DEFAULT_COLOR: String = '#33658A';
const HIGHLIGHT_COLOR: String = '#F6AE2D';
const VAR_LOCATION_PLACEHOLDER: String = window._varLocationPlaceholder;
const VAR_LOCATION_TITLE: String = window._varLocationTitle;
const LOADING_TEXT: String = window._loadingText;
const EMPTY_GEO_JSON: Object = {
    'type': 'FeatureCollection',
    'features': []  // Empty data for now
};


/**
 * Fetch Water Suggestion
 *
 * This method sends a request to the gcampus API to find nearby points
 * of interest with the tag "natural=water".
 *
 * @param lat {number|string} - Latitude
 * @param lng {number|string} - Longitude
 */
function fetchWaterSuggestion(lat, lng) {
    let url = '/api/v1/waterlookup/';
    // Parse string inputs for rounding later
    if (typeof lat !== 'number')
        lat = Number.parseFloat(lat);
    if (typeof lng !== 'number')
        lng = Number.parseFloat(lng);
    // Round the location to 3 digits. This should be precise enough
    // A large bounding box is used.
    // This improves cache performance
    let location = `POINT (${lng.toFixed(3)} ${lat.toFixed(3)})`;
    let bboxSize = '800';  // 800 meter square bounding box
    let params = {
        geo_center: location,
        geo_size: bboxSize
    };
    let searchParams = new URLSearchParams(params).toString();
    return fetch(`${url}?${searchParams}`)
        .then(response => response.json())
}


/**
 * Water List Item
 *
 * Returns an element used to display a list of water suggestions inside
 * the ``WaterList`` class.
 *
 * @param props
 * @returns {VNode}
 */
function ListItem(props) {
    let {feature, highlight, resetHighlight} = props;
    let name = feature.properties.name;
    let id = feature.id;
    return html`
        <label class="list-group-item list-group-item-action" for="water${id}"
               onMouseOver=${highlight} onMouseLeave=${resetHighlight}>
            <input class="form-check-input me-2" id="water${id}"
                   type="radio" name="water_name"
                   data-feature-id="${id}"
                   value="${name} gcampus_osm_id:${id}"/>
            ${name}
        </label>`;
}


class VariableWaterItem extends Component {
    constructor() {
        super();
        this.state = {name: ''};
    }

    setName(name) {
        this.setState({name: name});
    }

    setChecked(checked) {
        let el = document.getElementById('varWater');
        el.checked = checked;
        el.dispatchEvent(new Event("change"));
    }

    createNameChangeListener() {
        return (e) => {
            this.setChecked(true);
            let new_name = e.target.value;
            if (this.state.name !== new_name)
                this.setName(new_name);
        };
    }

    createClickListener() {
        return () => {
            this.setChecked(true);
        }
    }

    render(props, state, context) {
        let {name} = state;
        return html`
            <div class="list-group-item list-group-item-action"
                 onclick=${this.createClickListener()}>
                <input class="form-check-input me-2" id="varWater"
                       type="radio" name="water_name"
                       style="vertical-align: text-bottom"
                       value="${name}"
                       aria-label="${VAR_LOCATION_TITLE}" />
                ${VAR_LOCATION_TITLE}
                <input type="text"
                       id="inputLocationName"
                       class="form-control form-control-sm w-auto d-inline ms-2"
                       placeholder="${VAR_LOCATION_PLACEHOLDER}"
                       aria-label="${VAR_LOCATION_PLACEHOLDER}"
                       onInput=${this.createNameChangeListener()} />
            </div>`;
    }
}


class WaterList extends Component {
    state: Object;
    map;
    _layerID: String = 'waterLayer';
    _sourceID: String = 'waterList';
    _sourceIDHighlight: String = 'waterItemHighlighted';
    _layerIDHighlight: String = 'waterLayerHighlighted';
    _requestTimeout: ?Number = null;

    constructor() {
        super();
        this.state = {features: [], loading: false};
        this.currentPermanentHighlight = null;
        window.addEventListener('map:load', this.mapLoad.bind(this));
    }

    setFeatures(features) {
        this.setLoading(false);
        features = features || [];
        features = features.filter(
            f => f.properties.hasOwnProperty('name') && f.properties.name
        );
        this.map.getSource(this._sourceID).setData({
            'type': 'FeatureCollection',
            'features': features
        });
        if (this.currentPermanentHighlight !== null) {
            console.log(features);
            console.log(this.currentPermanentHighlight);
            let highlightedFeature = features.filter(
                f => this.validFeatureID(f.id) === this.validFeatureID(this.currentPermanentHighlight)
            );
            console.log(highlightedFeature);
            if (highlightedFeature.length === 0) {
                // The last selected water could not be found in the new
                // suggestion.
                // Thus, the selection is reset.
                console.log("reset");
                this.currentPermanentHighlight = null;
                this.resetHighlight();
            }
        }
        this.setState({features: features});
    }

    /**
     * Set Loading
     *
     * Set the loading state. Setting this to true will trigger display
     * the loading indicator.
     * @param loading
     */
    setLoading(loading) {
        this.setState({loading: loading});
    }

    /**
     * Valid Feature ID
     *
     * Returns a valid feature ID (i.e. an integer instead of a string)
     * and throws an exception if an invalid string or other type has
     * been provided.
     * This is needed because the feature layers use integer IDs whereas
     * the value of HTMLElements are strings.
     *
     * @param featureID {number|string}: Feature ID
     * @returns {number}
     */
    validFeatureID(featureID) {
        if (typeof featureID !== 'number') {
            try {
                return Number.parseInt(featureID);
            } catch {
                throw Error(`Unable to parse feature ID '${featureID}'. Expected an integer!`);
            }
        }
        return featureID;
    }

    /**
     * Get GeoJSON Feature
     *
     * Return the GeoJSON feature where the ID matches the passed
     * feature ID. Note that this will only return features that are
     * in the current state. Features that have been in the state
     * previously will not be returned.
     *
     * If a feature can not be found, an exception is thrown.
     *
     * @param featureID {Number|String}: Feature ID
     * @returns {Object} GeoJSON of the requested feature
     * @throws Error
     */
    getGeoJSONFeature(featureID: Number|String) {
        featureID = this.validFeatureID(featureID);
        let feature = this.state.features.filter(f => f.id === featureID);
        if (feature.length === 0) {
            throw Error(`Unable to find feature with ID ${featureID}!`);
        }
        if (feature.length > 1) {
            throw Error(`Found more than one feature with ID ${featureID}!`);
        }
        return feature[0];
    }

    /**
     * Highlight Feature
     *
     * Highlight a feature layer by a given ID. This will change the
     * color of the layer to visually distinguish one layer from the
     * others.
     *
     * @param featureID {number|string}: Feature ID
     */
    highlightFeature(featureID) {
        this.map.getSource(this._sourceIDHighlight).setData(
            this.getGeoJSONFeature(featureID)
        );
    }

    /**
     * Reset Highlight
     *
     * Resets the highlighting
     */
    resetHighlight() {
        // Set source data for the highlight layer to be empty
        this.map.getSource(this._sourceIDHighlight).setData(EMPTY_GEO_JSON);
        if (this.currentPermanentHighlight !== null) {
            this.highlightFeature(this.currentPermanentHighlight);
        }
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
        this.setLoading(true)
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
            fetchWaterSuggestion(lat, lng)
                .then(data => this.setFeatures(data.features))
                .catch(this.onError.bind(this));
        }, 300);
    }

    onError(err) {
        this.setLoading(false);
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
        this.map.addSource(this._sourceIDHighlight, {
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
                'line-color': DEFAULT_COLOR,
                'line-width': 3
            }
        });
        // Add highlight layer. This will automatically update once the
        // highlighted data source is set.
        this.map.addLayer({
            'id': this._layerIDHighlight,
            'type': 'line',
            'source': this._sourceIDHighlight,
            'layout': {},
            'paint': {
                'line-color': HIGHLIGHT_COLOR,
                'line-width': 4
            }
        });
        this.map.on('edit', this.mapUpdate.bind(this));
    }

    /**
     * Create mouseover Listener
     *
     * Returns a callable function that is used for registering event
     * listeners in the ``render`` method.
     *
     * @param feature {Object}: Feature object. Only the id attribute
     *      will be used.
     * @returns {(function(Event): void)}
     */
    createMouseOverListener(feature) {
        return (e) => {
            this.highlightFeature.bind(this)(feature.id);
        };
    }

    /**
     * Register Change Listener of Radio Buttons
     *
     * Iterates over all radio buttons and adds an event listener to
     * each. This will check if the radio button has been selected and
     * permanently highlights the features associated with those radio
     * buttons.
     */
    setupWaterList() {
        if (document.querySelector('input[name="water_name"]')) {
            document.querySelectorAll('input[name="water_name"]').forEach(el => {
                let featureID = null;
                if (el.id !== 'varWater') {
                    featureID = this.validFeatureID(
                        el.getAttribute("data-feature-id")
                    );
                }
                if (featureID === this.currentPermanentHighlight) {
                    el.checked = true;
                }
                el.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        // The element has actually been checked.
                        // All other elements will be ignored.

                        // If the current element is the variable water
                        // name item, then the variable below will be
                        // set to 'null'. Otherwise, it will have the
                        // correct ID.
                        this.currentPermanentHighlight = featureID;
                        // Reset highlight will remove all highlighting
                        // and highlight only the current selection
                        // given it is not null.
                        this.resetHighlight();
                    }
                });
            });
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        this.setupWaterList();
    }

    componentDidMount() {
        this.setupWaterList();
    }

    render(props, state, context) {
        let {features, loading} = state;
        let content = '';
        if (loading) {
            content = html`
                <div class="list-group-item">
                    <div class="spinner-border spinner-border-sm" role="status">
                    </div>
                    <span class="ms-2">${LOADING_TEXT}</span>
                </div>`
        } else {
            content = features.map(feature => html`
                <${ListItem}
                    feature=${feature}
                    highlight=${this.createMouseOverListener(feature)}
                    resetHighlight=${this.resetHighlight.bind(this)}
                />`
            );
        }
        return html`
            <div class="list-group bg-white"
                style="border-top-left-radius: 0; border-top-right-radius: 0;">
                ${content}
                <${VariableWaterItem} />
            </div>`;
    }
}


render(
    html`
        <${WaterList}/>`,
    document.getElementById('watersuggestion')
);

