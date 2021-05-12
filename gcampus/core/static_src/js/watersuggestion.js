import {Component, render} from 'preact';
import {html} from 'htm/preact';


const DEFAULT_COLOR = '#33658A';
const HIGHLIGHT_COLOR = '#F6AE2D';
const VAR_LOCATION_PLACEHOLDER = window._varLocationPlaceholder;
const VAR_LOCATION_TITLE = window._varLocationTitle;


/**
 * Fetch Water Suggestion
 *
 * This method sends a request to the gcampus API to find nearby points
 * of interest with the tag "natural=water".
 *
 * @param lat Number or String - Latitude
 * @param lng Number or String - Longitude
 */
function fetchWaterSuggestion(lat, lng) {
    let url = '/api/v1/geolookup/';
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


function ListItem(props) {
    let {feature, highlight, resetHighlight} = props;
    let name = feature.properties.name;
    let id = feature.id;
    return html`
        <label class="list-group-item list-group-item-action" for="water${id}"
               onMouseOver=${highlight} onMouseLeave=${resetHighlight}>
            <input class="form-check-input me-2" id="water${id}"
                   type="radio" name="location_name"
                   value="${id}"/>
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

    setLoading(loading) {
        this.setState({loading: loading});
    }

    updateStyle(layer, color) {
        let options = {
            fill: layer.options.fill,
            fillColor: color,
            fillOpacity: layer.options.fillOpacity,
            color: color
        }
        layer.setStyle(options);
    }

    getFeatureLayer(featureID) {
        let featureLayer = this.layer.getLayers().filter(
            l => l.feature.id === featureID
        );
        if (featureLayer.length !== 1) {
            throw Error(`Expected one layer with matching feature ID but got ${featureLayer.length}`);
        }
        return featureLayer[0];
    }

    highlightFeature(featureID) {
        let featureLayer = this.getFeatureLayer(featureID);
        this.updateStyle(featureLayer, HIGHLIGHT_COLOR);
    }

    resetHighlightFeature(featureID) {
        let featureLayer = this.getFeatureLayer(featureID);
        this.updateStyle(featureLayer, DEFAULT_COLOR);
    }

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

    mapInit(e) {
        this.map = e.detail.map;
        this.layer = L.geoJSON().addTo(this.map);
        this.map.on('draw:created draw:edited', this.mapUpdate.bind(this));
    }

    createMouseOverListener(feature) {
        return (e) => {
            this.highlightFeature.bind(this)(feature.id);
        };
    }

    createMouseLeaveListener(feature) {
        return (e) => {
            this.resetHighlightFeature.bind(this)(feature.id);
        };
    }

    render(props, state, context) {
        let {features, loading} = state;
        let spinner = '';
        if (loading) {
            spinner = html`
                <div class="list-group-item">
                    <div class="spinner-border spinner-border-sm" role="status">
                    </div>
                    <span class="ms-2">Loading...</span>
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

