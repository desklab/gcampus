import {Component, render} from 'preact';
import {html} from 'htm/preact';


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
    let url = '/api/v1/geolookup';
    let location = `${lat},${lng}`;
    let bboxSize = '100';  // 100 meter bounding box
    let params = {
        coords: location,
        size: bboxSize
    };
    let searchParams = new URLSearchParams(params).toString();
    return fetch(`${url}?${searchParams}`)
        .then(response => response.json())
}


class WaterList extends Component {
    constructor() {
        super();
        this.state = {features: []};
        window.addEventListener('map:init', this.mapInit.bind(this));
    }

    setFeatures(features) {
        this.setState({features: features});
    }

    mapUpdate(e) {
        let marker = e.layer;
        let {lat, lng} = marker.getLatLng();
        fetchWaterSuggestion(lat, lng)
            .then(data => this.setFeatures(data.features))
            .catch(console.error);
    }

    mapInit(e) {
        this.map = e.detail.map;
        this.map.on('draw:created draw:edited', this.mapUpdate.bind(this));
    }

    render(props, state, context) {
        let {features} = state;
        return html`
            <ul class="list-group bg-white"
                style="border-top-left-radius: 0; border-top-right-radius: 0;">
                ${features.map(feature => html`
                    <li class="list-group-item">
                        <input class="form-check-input"
                               type="radio" name="location_name"
                               value="${feature.id}"
                               aria-label="${feature.properties.name}"/>
                        <span class="ms-2">${feature.properties.name}</span>
                    </li>`
                )}
            </ul>`;
    }
}

render(
    html`
        <${WaterList}/>`,
    document.getElementById('watersuggestion')
);

