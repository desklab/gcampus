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


function getContentElement(parent, contentType) {
    return parent.querySelector('[data-content-type="' + contentType + '"]');
}

function createMeasurementPopup(coords, map, data, template) {
    let popup = new mapboxgl.Popup()
        .setLngLat(coords)
        .setHTML(template)
        .addTo(map);
    let item = popup.getElement().querySelector('.mapboxgl-popup-content');
    let {name, time, parameters, url, water} = data.properties;
    let waterName = water.display_name;
    item.querySelector('a').setAttribute('href', url);
    getContentElement(item, 'waterName').innerText = waterName;
    if (name === "" || name === undefined || name === null) {
        getContentElement(item, 'measurementName').parentElement.remove();
    } else {
        getContentElement(item, 'measurementName').innerText = name;
    }
    getContentElement(item, 'measurementTime').innerText = (
        new Date(time).toLocaleString()
    );
    let parameterIndicators = getContentElement(item, 'parameterList');
    for (let parameter of parameters) {
        let container = document.createElement('div');
        container.classList.add('indicator-container');
        let icon = document.createElement('i');
        icon.classList.add('circle-icon', 'indicator-icon');
        icon.setAttribute(
            'style',
            'background-color: #'
            + String(parameter.parameter_type.color).toLowerCase()
            + ' !important;'
        );
        icon.setAttribute('title', String(parameter.parameter_type.name));
        icon.setAttribute('data-bs-toggle', 'tooltip');
        container.insertAdjacentElement('afterbegin', icon);
        parameterIndicators.insertAdjacentElement('beforeend', container);
        try {
            new gcampuscore.main.Tooltip(icon);
        } catch (e) {
            console.error('Unable to call `gcampuscore.main.Tooltip`');
        }
    }
}

/**
 *
 * @param counts {{running: number, standing: number, unknown: number}}
 * @param colors {{running: string, standing: string, unknown: string}}
 * @returns {HTMLDivElement}
 */
function createPieChart(counts, colors) {
    let offsets = {}, total = 0;
    for (let flowType in counts) {
        offsets[flowType] = total;
        total += counts[flowType];
    }
    let fontSize, radius;
    if (total >= 100) {
        fontSize = 22;
        radius = 60;
    } else if (total >= 50) {
        fontSize = 20;
        radius = 45;
    } else if (total >= 10) {
        fontSize = 18;
        radius = 35;
    } else {
        fontSize = 16;
        radius = 25;
    }
    const r0 = Math.round(radius * 0.6);
    const size = String(radius * 2);

    let container = document.createElement('div');
    let svgParent = document.createElementNS(
        'http://www.w3.org/2000/svg', 'svg'
    );
    svgParent.setAttributeNS(null, 'width', size);
    svgParent.setAttributeNS(null, 'height', size);
    svgParent.setAttributeNS(null, 'viewbox', [0, 0, size, size].join(' '));
    svgParent.setAttributeNS(null, 'text-anchor', 'middle');
    svgParent.setAttributeNS(null, 'style',
        'font: '
        + String(fontSize)
        + 'px sans-serif; display: block; cursor: pointer;'
    );

    let bgCircle = document.createElementNS(
        'http://www.w3.org/2000/svg', 'circle'
    );
    bgCircle.setAttributeNS(null, 'cx', String(radius));
    bgCircle.setAttributeNS(null, 'cy', String(radius));
    bgCircle.setAttributeNS(null, 'r', String(radius));
    bgCircle.setAttributeNS(null, 'fill', 'white');
    svgParent.appendChild(bgCircle);

    for (let flowType in counts) {
        let count = counts[flowType];
        if (count <= 0) continue;
        let start = offsets[flowType];
        let end = start + count;
        svgParent.appendChild(
            pieSegment(total, start, end, radius - 4, radius, colors[flowType])
        );
    }
    let textElement = document.createElementNS(
        'http://www.w3.org/2000/svg', 'text'
    );
    textElement.setAttributeNS(null, 'dominant-baseline', 'central');
    textElement.setAttributeNS(null, 'color', 'white');
    textElement.setAttributeNS(null, 'fill', 'white');
    textElement.setAttributeNS(null, 'transform',
        'translate(' + [radius, radius].join(', ') + ')'
    );
    textElement.textContent = total.toLocaleString();
    svgParent.appendChild(textElement);
    container.appendChild(svgParent);
    return container;
}

/**
 * @param total {number}
 * @param start {number}
 * @param end {number}
 * @param radius {number}
 * @param center {number}
 * @param color {string}
 * @returns {SVGCircleElement}
 */
function pieSegment(
    total,
    start,
    end,
    radius,
    center,
    color) {
    const circleSegment = document.createElementNS(
        'http://www.w3.org/2000/svg', 'circle'
    );
    let percentage = (end - start) / total;
    let strokeDashArray = [
        Math.PI * radius * percentage,
        Math.PI * radius
    ];
    let rotation = (start / total) * 360 - 90;
    circleSegment.setAttributeNS(null, 'r', String(radius / 2));
    circleSegment.setAttributeNS(null, 'cx', String(center));
    circleSegment.setAttributeNS(null, 'cy', String(center));
    circleSegment.setAttributeNS(null, 'fill', 'transparent');
    circleSegment.setAttributeNS(null, 'stroke', color);
    circleSegment.setAttributeNS(null, 'stroke-width', String(radius));
    circleSegment.setAttributeNS(null, 'stroke-dasharray', strokeDashArray.join(' '));
    circleSegment.setAttributeNS(null, 'transform',
        'rotate(' + [rotation, center, center].join(' ') + ')'
    );
    return circleSegment;
}


/**
 *
 * @param url {String}
 * @param map {mapboxgl.Map}
 */
function setupCluster(url, map) {
    const measurementPopupTemplate = (
        document.getElementById('measurementPopupTemplate').text
    );
    const rootStyle = getComputedStyle(document.documentElement);
    const unknownColor = rootStyle.getPropertyValue('--gcampus-unknown-water');
    const runningCase = ['==', ['get', 'water_flow_type'], 'running'];
    const runningColor = rootStyle.getPropertyValue('--gcampus-running-water');
    const standingCase = ['==', ['get', 'water_flow_type'], 'standing'];
    const standingColor = rootStyle.getPropertyValue(
        '--gcampus-standing-water'
    );
    const colors = {
        standing: standingColor,
        running: runningColor,
        unknown: unknownColor
    };
    map.addSource('measurements', {
        type: 'geojson',
        data: url,
        cluster: true,
        // Max zoom to cluster points on
        clusterMaxZoom: 14,
        // Radius of each cluster when clustering points
        clusterRadius: 50,
        clusterProperties: {
            'running': ['+', ['case', runningCase, 1, 0]],
            'standing': ['+', ['case', standingCase, 1, 0]],
        }
    });
    map.addLayer({
        'id': 'markers',
        'type': 'circle',
        'source': 'measurements',
        'filter': ['!=', 'cluster', true],
        'paint': {
            'circle-color': [
                'case',
                runningCase,
                runningColor,
                standingCase,
                standingColor,
                unknownColor
            ],
            'circle-radius': 8,
            'circle-stroke-width': 3,
            'circle-stroke-color': '#ffffff'
        }
    });

    const markers = {};
    let visibleMarkers = {};

    function updateMarkers() {
        if (!map.isSourceLoaded('measurements')) return;
        const newMarkers = {};
        const features = map.querySourceFeatures('measurements');

        // for every cluster on the screen, create an HTML marker for it
        // (if it does not yet exist),
        // and add it to the map if it's not there already
        for (const feature of features) {
            const coords = feature.geometry.coordinates;
            const props = feature.properties;
            if (!props.cluster) continue;
            const id = props.cluster_id;
            let marker = markers[id];
            if (!marker) {
                let {running, standing, point_count} = props;
                let counts = {
                    'running': running,
                    'standing': standing,
                    'unknown': point_count - running - standing
                };
                const el = createPieChart(counts, colors);
                marker = markers[id] = new mapboxgl.Marker({
                    element: el
                }).setLngLat(coords);
                el.addEventListener('click', () => {
                    let zoom = map.getZoom() + 2;
                    let maxZoom = map.getMaxZoom();
                    map.flyTo({
                        center: coords,
                        zoom: (zoom <= maxZoom) ? zoom : maxZoom
                    });
                });
            }
            newMarkers[id] = marker;

            if (!visibleMarkers[id]) marker.addTo(map);
        }
        // for every marker we've added previously, remove those that are no longer visible
        for (const id in visibleMarkers) {
            if (!newMarkers[id]) visibleMarkers[id].remove();
        }
        visibleMarkers = newMarkers;
    }

    // after the GeoJSON data is loaded, update markers on the screen
    // on every frame
    map.on('render', updateMarkers);

    map.on('mouseenter', 'markers', () => {
        map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'markers', () => {
        map.getCanvas().style.cursor = '';
    });

    let measurementCache = {};
    let detailApiUrl = url;
    if (detailApiUrl.slice(-1) !== '/') {
        detailApiUrl += '/';
    }
    map.on('click', 'markers', (e) => {
        let coordinates = e.features[0].geometry.coordinates.slice();
        // Ensure that if the map is zoomed out such that
        // multiple copies of the feature are visible, the
        // popup appears over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }
        let measurementId = e.features[0].id;
        let data = measurementCache[measurementId];
        if (!data) {
            fetch(detailApiUrl + String(measurementId) + '/', {
                method: 'get',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                },
                redirect: 'follow',
                referrerPolicy: 'no-referrer',
            }).then(response => response.json())
                .then(data => {
                    measurementCache[measurementId] = data;
                    createMeasurementPopup(coordinates, map, data, measurementPopupTemplate);
                });
        } else{
            createMeasurementPopup(coordinates, map, data, measurementPopupTemplate);
        }
    });
}

export {setupCluster};
