import {
    ArcElement,
    CategoryScale,
    Chart,
    Decimation,
    Filler,
    Legend,
    LinearScale,
    LineController,
    LineElement,
    LogarithmicScale,
    PointElement,
    ScatterController,
    SubTitle,
    Title,
    Tooltip
} from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';


Chart.register(
    ArcElement,
    LineElement,
    PointElement,
    LineController,
    ScatterController,
    CategoryScale,
    LinearScale,
    LogarithmicScale,
    Decimation,
    Filler,
    Legend,
    Title,
    Tooltip,
    SubTitle,
    annotationPlugin,
);


function makeArr(startValue, stopValue, cardinality) {
    var arr = [];
    var step = (stopValue - startValue) / (cardinality - 1);
    for (var i = 0; i < cardinality; i++) {
        arr.push(startValue + (step * i));
    }
    return arr;
}

let _functionCache = {};


function convert(pk, value) {
    if (!_functionCache.hasOwnProperty(pk)) {
        throw Error(
            'Parameter ' + String(pk) + ' has not been initialized yet!'
        );
    }
    return _functionCache[pk](value).toFixed(2);
}


function createChart(pk, el, formula, title, x_label, y_label, x_max, x_min) {

    x_min = parseFloat(x_min);
    x_max = parseFloat(x_max);
    _functionCache[pk] = new Function(
        '\'use strict\'; let od = arguments[0]; return ' + String(formula) + ';'
    );
    let x_data = [];
    let y_data = makeArr(0, 1.6, 17);
    for (let i = 0; i < y_data.length; i++) {
        let x = convert(pk, y_data[i]);
        x_data.push(parseFloat(x));
    }
    if (x_max == -9999) {
        x_max = parseFloat(x_data[x_data.length - 1]);
    }
    if (x_min == -9999) {
        x_min = parseFloat(x_data[0]);
    }

    var y_max = 1.6;
    return new Chart(el.getContext('2d'), {
        type: 'line',
        data: {
            labels: x_data,
            datasets: [{
                data: y_data,
                borderColor: '#3e95cd',
                fill: false
            },
            ]
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    max: x_max,
                    min: x_min,
                    ticks: {},
                    title: {
                        display: true,
                        text: x_label
                    }
                },
                y: {
                    max: y_max,
                    ticks: {},
                    title: {
                        display: true,
                        text: y_label
                    }
                },
            },
            elements: {
                point: {
                    radius: 1,
                    display: true
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                autocolors: false,
                annotation: {
                    annotations: {
                        point1: {
                            display: false,
                            type: 'point',
                            xValue: 0,
                            yValue: 0,
                            backgroundColor: 'rgba(13, 110, 253, 0.25)'
                        }
                    }
                },
                title: {
                    display: true,
                    text: title
                }
            }

        }
    });
}


function updateAnnotation(x, y, chart) {
    chart.options.plugins.annotation.annotations.point1.xValue = x;
    chart.options.plugins.annotation.annotations.point1.yValue = y;
    chart.options.plugins.annotation.annotations.point1.display = true;
    chart.update();
}

export {createChart, updateAnnotation, convert};
