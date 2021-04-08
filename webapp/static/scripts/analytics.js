document.addEventListener('DOMContentLoaded', function () {
const chart = Highcharts.chart('chart-container', {
    chart: {
        type: 'line'
    },
    title: {
        text: ""
    },
    legend: {
        enabled:false
    },
    xAxis: {
        categories: ['Wed 15th','Wed 16th','Wed 17th','Wed 18th','Wed 19th','Wed 20th','Wed 21th','Wed 22th', 'Wed 23th', 'Wed 24th', 'Wed 25th', 'Wed 26th', 'Wed 27th', 'Wed 28th'],
        tickInterval: 1,
        tickLength: 10,
        tickWidth: 1
    },
    yAxis: {
        gridLineColor: 'transparent',
        title: {
            text: null
        },
        labels: {
            "label" : "label"
        }
    },
    series: [{
        name: 'Wed 15th',
        data: [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    }],
    responsive: {
        rules: [{
            condition: {
                maxWidth: 999
            },
            chartOptions: {
                xAxis: {
                    tickInterval: 3
                }
            }
        },
        {
            condition: {
                maxWidth: 600
            },
            chartOptions: {
                xAxis: {
                    tickInterval: 4
                }
            }
        },
        {
            condition: {
                maxWidth: 400
            },
            chartOptions: {
                xAxis: {
                    tickInterval: 5
                }
            }
        }
    ]
    }
});
});