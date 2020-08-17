function chart_draw_line_bar_color(ec, div_id, title, yAxis_left_name, yAxis_right_name, x_datas, color_pieces, series) {
    // 基于准备好的dom，初始化echarts图表
    var myChart = ec.init(document.getElementById(div_id));

    var option = {
        title: {
            text: title
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data:[yAxis_left_name,yAxis_right_name]
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType: {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : [
            {
                type: 'inside',
                start: 0,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                top: '90%',
                start: 0,
                end: 100
            }
        ],
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : x_datas
            }
        ],
        yAxis : [
            {
                type : 'value',
                name : yAxis_left_name,
                scale:true,
                position: 'left',
                boundaryGap: [0.01, 0.01]
            },
            {
                type: 'value',
                name: yAxis_right_name,
                scale:true,
                position: 'right',
            },
        ],
        visualMap: {
            show: false,
            dimension: 0,
            seriesIndex: 1,
            pieces: color_pieces
        },
        series :
            series
    };

    // 为echarts对象加载数据
    myChart.setOption(option);
}

function chart_draw_line_bar(ec, div_id, title, yAxis_left_name, yAxis_right_name, x_datas, series) {
    // 基于准备好的dom，初始化echarts图表
    var myChart = ec.init(document.getElementById(div_id));

    var option = {
        title: {
            text: title
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data:[yAxis_left_name,yAxis_right_name]
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType: {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : [
            {
                type: 'inside',
                start: 0,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                top: '90%',
                start: 0,
                end: 100
            }
        ],
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : x_datas
            }
        ],
        yAxis : [
            {
                type : 'value',
                name : yAxis_left_name,
                scale:true,
                position: 'left',
                boundaryGap: [0.01, 0.01]
            },
            {
                type: 'value',
                name: yAxis_right_name,
                scale:true,
                position: 'right',
            },
        ],
        series :
            series
    };

    // 为echarts对象加载数据
    myChart.setOption(option);
}

function chart_draw_double_bar(ec, div_id, title, legend, yAxis_name, x_datas, series) {
    // 基于准备好的dom，初始化echarts图表
    var myChart = ec.init(document.getElementById(div_id));

    var option = {
        title: {
            text: title
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data:legend
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType: {show: true, type: ['bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : [
            {
                type: 'inside',
                start: 0,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                top: '90%',
                start: 0,
                end: 100
            }
        ],
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : x_datas
            }
        ],
        yAxis : [
            {
                type : 'value',
                name : yAxis_name,
                scale:true,
                position: 'left',
                boundaryGap: [0.01, 0.01]
            },
        ],
        series :
            series
    };

    // 为echarts对象加载数据
    myChart.setOption(option);
}

function chart_draw_four_y_axis(ec, div_id, title, axis_names, legend, x_datas, series) {
    var myChart = ec.init(document.getElementById(div_id));

    var option = {
        animation:false,
        calculable:false,
        title: {
            text: title,
            x: 'center'
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            x: 'left',
            data:legend
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType: {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        axisPointer: {
            link: [{
                xAxisIndex: [0, 1]
            }]
        },
        dataZoom : [
            {
                type: 'inside',
                xAxisIndex: [0, 1],
                start: 0,
                end: 100
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                top: '90%',
                start: 0,
                end: 100
            }
        ],
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : x_datas
            },
            {
                type : 'category',
                gridIndex : 1,
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                position: 'bottom',
                data : x_datas
            }
        ],
        yAxis : [
            {
                type : 'value',
                name : axis_names[0],
                scale : 'true',
            },
            {
                type : 'value',
                gridIndex: 0,
                name : axis_names[1],
                scale : 'true',
            },
            {
                type : 'value',
                gridIndex : 1,
                name : axis_names[2]
            },
            {
                type : 'value',
                gridIndex : 1,
                name : axis_names[3]
            },
        ],
        grid: [{
            height: '40%'
        }, {
            height: '25%',
            top: "60%"
        }],
        series :
            series
    };

    // 为echarts对象加载数据
    myChart.setOption(option);
}

function chart_draw_two_line_bar(ec, div_id, title, axis_names, legend, x_datas, series)
{
    var myChart = ec.init(document.getElementById(div_id));

    var option = {
        animation:false,
        calculable:false,
        title: {
            text: title,
            x: 'center'
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            x: 'left',
            data:legend
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType: {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : [
            {
                type: 'inside',
                start: 0,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                top: '90%',
                start: 0,
                end: 100
            }
        ],
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : x_datas
            }
        ],
        yAxis : [
            {
                type : 'value',
                name : axis_names[0],
                scale : 'true',
            },
            {
                type : 'value',
                name : axis_names[1],
                scale : 'true',
            },
        ],
        series :
            series
    };

    // 为echarts对象加载数据
    myChart.setOption(option);
}

function chart_draw_bar(ec, div_id, title, yAxis_name, x_datas, series)
{
    // 基于准备好的dom，初始化echarts图表
    var myChart = ec.init(document.getElementById(div_id));

    var option = {
        animation:false,
        calculable:false,
        title: {
            text: title,
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data:[yAxis_name]
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType: {show: true, type: ['bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : [
            {
                type: 'inside',
                start: 0,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                top: '90%',
                start: 0,
                end: 100
            }
        ],
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : x_datas
            }
        ],
        yAxis : [
            {
                type : 'value',
                name : yAxis_name,
                scale : 'true'
            }
        ],
        series :
            series
    };

    // 为echarts对象加载数据
    myChart.setOption(option);
}

function chart_draw_line(ec, div_id, title, legend, yAxis_name, x_datas, series)
{
    // 基于准备好的dom，初始化echarts图表
    var myChart = ec.init(document.getElementById(div_id));

    var option = {
        animation:false,
        calculable:false,
        title: {
            text: title,
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data:legend
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType: {show: true, type: ['line']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : [
            {
                type: 'inside',
                start: 0,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                top: '90%',
                start: 0,
                end: 100
            }
        ],
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : x_datas
            }
        ],
        yAxis : [
            {
                type : 'value',
                name : yAxis_name,
                scale : 'true'
            }
        ],
        series :
            series
    };

    // 为echarts对象加载数据
    myChart.setOption(option);
}

function chart_draw_k(ec, div_id, title, yAxis_name, x_datas, series)
{
    var myChart = ec.init(document.getElementById(div_id));

    var option = {
        animation:false,
        calculable:false,
        title: {
            text: title,
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
               type: 'cross'
            }
        },
        legend: {
            data:[yAxis_name]
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType: {show: true, type: ['k']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : [
            {
                type: 'inside',
                start: 0,
                end: 10
            },
            {
                type: 'slider',
                start: 0,
                end: 10
            }
        ],
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : x_datas
            }
        ],
        yAxis : [
            {
                type : 'value',
                scale:true,
                name : yAxis_name,
            }
        ],
        series :
            series
    };

    myChart.setOption(option);
}