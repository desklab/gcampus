import { GeoSearchControl, OpenStreetMapProvider } from 'leaflet-geosearch';
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

// export {search};
