import {Component, render} from 'preact';
import {html} from 'htm/preact';


const DEFAULT_COLOR = '#33658A';
const HIGHLIGHT_COLOR = '#F6AE2D';
const VAR_LOCATION_PLACEHOLDER = window._varLocationPlaceholder;
const VAR_LOCATION_TITLE = window._varLocationTitle;
const LOADING_TEXT = window._loadingText;


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
    let url = '/api/v1/geolookup/';
    // Parse string inputs for rounding later
    if (typeof lat !== 'number')
        lat = Number.parseFloat(lat);
    if (typeof lng !== 'number')
        lng = Number.parseFloat(lng);
    // Round the location to 3 digits. This should be precise enough
    // A large bounding box is used.
    // This improves cache performance
    let location = `${lat.toFixed(3)},${lng.toFixed(3)}`;
    let bboxSize = '800';  // 800 meter square bounding box
    let params = {
        coords: location,
        size: bboxSize
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
                   type="radio" name="location_name"
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
                       type="radio" name="location_name"
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
    constructor() {
        super();
        this.state = {features: [], loading: false};
        this.currentPermanentHighlight = null;
        window.addEventListener('map:init', this.mapInit.bind(this));
    }

    setFeatures(features) {
        this.setLoading(false);
        this.layer.clearLayers();
        features = features || [];
        features = features.filter(
            f => f.properties.hasOwnProperty('name') && f.properties.name
        );
        if (features.hasOwnProperty('length') && features.length > 0) {
            this.layer.addData(features);
            this.layer.setStyle({color: DEFAULT_COLOR});
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
     * Update Style
     *
     * Update the styling (fill and edge color) of a feature layer.
     * Used to highlight and reset features once they are hovered or
     * selected.
     *
     * @param layer: Map layer of the feature
     * @param color {String}: Fill and edge color
     */
    updateStyle(layer, color) {
        let options = {
            fill: layer.options.fill,
            fillColor: color,
            fillOpacity: layer.options.fillOpacity,
            color: color
        }
        layer.setStyle(options);
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
     * Get Feature Layer
     *
     * Return the feature layer for a given feature ID. If no layer with
     * matching ID can be found, an error is thrown.
     *
     * @param featureID {number|string}: Feature ID
     * @returns: A map layer
     */
    getFeatureLayer(featureID) {
        featureID = this.validFeatureID(featureID);
        let featureLayer = this.layer.getLayers().filter(
            l => l.feature.id === featureID
        );
        if (featureLayer.length !== 1) {
            throw Error(`Expected one layer with matching feature ID but got ${featureLayer.length}`);
        }
        return featureLayer[0];
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
        let featureLayer = this.getFeatureLayer(featureID);
        this.updateStyle(featureLayer, HIGHLIGHT_COLOR);
    }

    /**
     * Reset Highlight Feature
     *
     * Resets the highlighting of a given feature. This will always
     * remove the highlighting, whether or not the feature is
     * permanently highlighted (e.g. by being selected).
     *
     * @param featureID {number|string}: Feature ID
     */
    resetHighlightFeature(featureID) {
        let featureLayer = this.getFeatureLayer(featureID);
        this.updateStyle(featureLayer, DEFAULT_COLOR);
    }

    /**
     *  Maybe Reset Highlight Feature
     *
     *  Only resets the highlighting of a given feature if the feature
     *  is not currently permanently highlighted. Used for when the
     *  element is no longer hovered.
     *
     * @param featureID {number|string}: Feature ID
     */
    maybeResetHighlightFeature(featureID) {
        if (this.validFeatureID(featureID) === this.validFeatureID(this.currentPermanentHighlight)) {
            // Do nothing
            return;
        }
        this.resetHighlightFeature(featureID);
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
        this.setFeatures([]);
        let marker = e.layer;
        let {lat, lng} = marker.getLatLng();
        this.setLoading(true)
        fetchWaterSuggestion(lat, lng)
            .then(data => this.setFeatures(data.features))
            .catch(this.onError.bind(this));
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
    mapInit(e) {
        this.map = e.detail.map;
        this.layer = L.geoJSON().addTo(this.map);
        this.map.on('draw:created draw:edited', this.mapUpdate.bind(this));
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
     * Create mouseleave Listener
     *
     * Returns a callable function that is used for registering event
     * listeners in the ``render`` method.
     *
     * @param feature {Object}: Feature object. Only the id attribute
     *      will be used.
     * @returns {(function(Event): void)}
     */
    createMouseLeaveListener(feature) {
        return (e) => {
            this.maybeResetHighlightFeature.bind(this)(feature.id);
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
    registerChangeListener() {
        if (document.querySelector('input[name="location_name"]')) {
            document.querySelectorAll('input[name="location_name"]').forEach(el => {
                el.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        // The element has actually been checked
                        if (this.currentPermanentHighlight) {
                            // There was a previously checked element
                            // that has been permanently highlighted.
                            // Reset the highlighting of the old
                            // feature.
                            this.resetHighlightFeature(this.currentPermanentHighlight)
                        }
                        if (e.target.id !== 'varWater') {
                            // The element has a feature ID associated
                            // with it.
                            let featureID = e.target.getAttribute("data-feature-id");
                            this.highlightFeature(featureID);
                            this.currentPermanentHighlight = featureID;
                        } else {
                            // The element is a variable water name item
                            // and thus has no feature associated with
                            // it.
                            this.currentPermanentHighlight = null;
                        }
                    }
                });
            });
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        this.registerChangeListener();
    }

    componentDidMount() {
        this.registerChangeListener();
    }

    render(props, state, context) {
        let {features, loading} = state;
        let spinner = '';
        if (loading) {
            spinner = html`
                <div class="list-group-item">
                    <div class="spinner-border spinner-border-sm" role="status">
                    </div>
                    <span class="ms-2">${LOADING_TEXT}</span>
                </div>`
        }
        return html`
            <div class="list-group bg-white"
                style="border-top-left-radius: 0; border-top-right-radius: 0;">
                ${features.map(feature => html`
                    <${ListItem}
                            feature=${feature}
                            highlight=${this.createMouseOverListener(feature)}
                            resetHighlight=${this.createMouseLeaveListener(feature)}
                    />
                `)}
                ${spinner}
                <${VariableWaterItem} />
            </div>`;
    }
}


render(
    html`
        <${WaterList}/>`,
    document.getElementById('watersuggestion')
);

