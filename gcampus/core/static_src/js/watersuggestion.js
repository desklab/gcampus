import {Component, render} from 'preact';
import {html} from 'htm/preact';


const DEFAULT_COLOR = '#33658A';
const HIGHLIGHT_COLOR = '#F6AE2D';


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
        <li class="list-group-item list-group-item-action"
            onMouseOver=${highlight} onMouseLeave=${resetHighlight}>
            <input class="form-check-input"
                   type="radio" name="location_name"
                   value="${id}"
                   aria-label="${name}"/>
            <span class="ms-2">${name}</span>
        </li>`;
}


class WaterList extends Component {
    constructor() {
        super();
        this.state = {features: []};
        window.addEventListener('map:init', this.mapInit.bind(this));
    }

    setFeatures(features) {
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
        fetchWaterSuggestion(lat, lng)
            .then(data => this.setFeatures(data.features))
            .catch(console.error);
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
        let {features} = state;
        return html`
            <ul class="list-group bg-white"
                style="border-top-left-radius: 0; border-top-right-radius: 0;">
                ${features.map(feature => html`
                    <${ListItem}
                            feature=${feature}
                            highlight=${this.createMouseOverListener(feature)}
                            resetHighlight=${this.createMouseLeaveListener(feature)}
                    />
                `)}
            </ul>`;
    }
}

render(
    html`
        <${WaterList}/>`,
    document.getElementById('watersuggestion')
);

