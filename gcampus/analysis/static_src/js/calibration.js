import {
    Chart,
    ArcElement,
    LineElement,
    BarElement,
    PointElement,
    BarController,
    BubbleController,
    DoughnutController,
    LineController,
    PieController,
    PolarAreaController,
    RadarController,
    ScatterController,
    CategoryScale,
    LinearScale,
    LogarithmicScale,
    RadialLinearScale,
    TimeScale,
    TimeSeriesScale,
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
    BarElement,
    PointElement,
    BarController,
    BubbleController,
    DoughnutController,
    LineController,
    PieController,
    PolarAreaController,
    RadarController,
    ScatterController,
    CategoryScale,
    LinearScale,
    LogarithmicScale,
    RadialLinearScale,
    TimeScale,
    TimeSeriesScale,
    Decimation,
    Filler,
    Legend,
    Title,
    Tooltip,
    SubTitle,
    annotationPlugin,
);


function createChart(name, el, slope, offset, title, x_label, y_label) {
    let x_data = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
    let y_data = []
    for (let i = 0; i < x_data.length; i++) {
        let val = x_data[i] * slope + offset;
        y_data.push(val);

    }
    const max_y = y_data.slice(-1)[0] + 5
    return new Chart(el.getContext("2d"), {
        type: 'line',
        data: {
            labels: x_data,
            datasets: [{
                data: y_data,
                borderColor: "#3e95cd",
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
                    max: x_data.length + 2,
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
    // Times 4 since the chart.js x values do not correspond to the xdata but
    // rather to the number of of the datapoint e.g. 0,25 = 1, 0,5 = 2, ...
    chart.options.plugins.annotation.annotations.point1.xValue = x * 4;
    chart.options.plugins.annotation.annotations.point1.yValue = y;
    chart.options.plugins.annotation.annotations.point1.display = true;
    chart.update();
}

export {createChart, updateAnnotation};