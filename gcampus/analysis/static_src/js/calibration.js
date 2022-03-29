import {
    Chart,
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
    SubTitle
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


function createChart(name, el, formula, title, x_label, y_label) {
    let x_data = [];
    let y_data = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5];
    for (let i = 0; i < y_data.length; i++) {
        let od = y_data[i];  // noqa: od is used in eval.
        let x = eval(formula).toFixed(2);
        x_data.push(x);
    }
    const max_y = 1.6;
    const max_x = x_data.max;
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
                y: {
                    max: max_y,
                    min: 0,
                    ticks: {},
                    title: {
                        display: true,
                        text: y_label
                    }
                },
                x: {
                    max: max_x,
                    min: 0,
                    ticks: {},
                    title: {
                        display: true,
                        text: x_label
                    }
                }
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
    // Needs calculation since the chart.js x values do not correspond
    // to the xdata but has to be scaled relative to the axis labels
    let len = chart.data.labels.length -1;
    let x_max = parseFloat(chart.data.labels[len]);
    chart.options.plugins.annotation.annotations.point1.xValue = len*x/x_max;
    chart.options.plugins.annotation.annotations.point1.yValue = y;
    chart.options.plugins.annotation.annotations.point1.display = true;
    chart.update();
}

export {createChart, updateAnnotation};
