/*=========================================================================================
    File Name: dashboard-ecommerce.js
    Description: dashboard-ecommerce
    ----------------------------------------------------------------------------------------
    Item Name: Chameleon Admin - Modern Bootstrap 4 WebApp & Dashboard HTML Template + UI Kit
    Version: 1.0
    Author: ThemeSelection
    Author URL: https://themeselection.com/
==========================================================================================*/


(function (window, document, $) {

    /*************************************************
    *               Line gradient chart               *
    *************************************************/

    var lineGradientChart1 = new Chartist.Line('#gradient-line-chart1', {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        series: [
            [125, 200, 125, 225, 175, 275, 220],
            [175, 275, 165, 280, 120, 226, 150]
        ]
    }, {
            low: 100,
            fullWidth: true,
            onlyInteger: true,
            axisY: {
                low: 0,
                scaleMinSpace: 50,
            },
            axisX: {
                showGrid: false
            },
            lineSmooth: Chartist.Interpolation.simple({
                divisor: 2
            })
        });
    lineGradientChart1.on('created', function (data) {
        var defs = data.svg.querySelector('defs') || data.svg.elem('defs');
        defs.elem('linearGradient', {
            id: 'lineLinear1',
            x1: 0,
            y1: 0,
            x2: 1,
            y2: 0
        }).elem('stop', {
            offset: '0%',
            'stop-color': 'rgba(168,120,244,0.1)'
        }).parent().elem('stop', {
            offset: '10%',
            'stop-color': 'rgba(168,120,244,1)'
        }).parent().elem('stop', {
            offset: '80%',
            'stop-color': 'rgba(255,108,147, 1)'
        }).parent().elem('stop', {
            offset: '98%',
            'stop-color': 'rgba(255,108,147, 0.1)'
        });

        defs.elem('linearGradient', {
            id: 'lineLinear2',
            x1: 0,
            y1: 0,
            x2: 1,
            y2: 0
        }).elem('stop', {
            offset: '0%',
            'stop-color': 'rgba(0,230,175,0.1)'
        }).parent().elem('stop', {
            offset: '10%',
            'stop-color': 'rgba(0,230,175,1)'
        }).parent().elem('stop', {
            offset: '80%',
            'stop-color': 'rgba(255,161,69, 1)'
        }).parent().elem('stop', {
            offset: '98%',
            'stop-color': 'rgba(255,161,69, 0.1)'
        });

        return defs;


    }).on('draw', function (data) {
        var circleRadius = 10;
        if (data.type === 'point') {
            var circle = new Chartist.Svg('circle', {
                cx: data.x,
                cy: data.y,
                'ct:value': data.y,
                r: circleRadius,
                class: data.value.y === 225 ? 'ct-point ct-point-circle' : 'ct-point ct-point-circle-transperent'
            });
            data.element.replace(circle);
        }
        if (data.type === 'line') {
            data.element.animate({
                d: {
                    begin: 1000,
                    dur: 1000,
                    from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
                    to: data.path.clone().stringify(),
                    easing: Chartist.Svg.Easing.easeOutQuint
                }
            });
        }
    });

    
})(window, document, jQuery);
