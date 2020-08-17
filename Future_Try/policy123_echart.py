template ="""
<!DOCTYPE html>
<head>
    <meta charset="utf-8">
    <title>123策略</title>
</head>
<body>
    <!-- 为ECharts准备一个具备大小（宽高）的Dom -->
    <div id="main" style="height:400px"></div>
    <!-- ECharts单文件引入 -->
    <script src="http://echarts.baidu.com/build/dist/echarts.js"></script>
    <script type="text/javascript">
        // 路径配置
        require.config({
            paths: {
                echarts: 'http://echarts.baidu.com/build/dist'
            }
        });

        // 使用
        require(
            [
                'echarts',
                'echarts/chart/bar', // 使用柱状图就加载bar模块，按需加载
                'echarts/chart/k',
                'echarts/chart/line'

            ],
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                var myChart = ec.init(document.getElementById('main'));

                var option = {
                     tooltip : {
                        trigger: 'axis',
                        formatter: function (params) {
                            var res = params[0].seriesName + ' ' + params[0].name;
                            res += '<br/>  开盘 : ' + params[0].value[0] + '  最高 : ' + params[0].value[3];
                            res += '<br/>  收盘 : ' + params[0].value[1] + '  最低 : ' + params[0].value[2];

                            res += '<br/>' + params[1].seriesName + ':' + params[1].value;
                            res += '<br/>' + params[2].seriesName + ':' + params[2].value;
                            res += '<br/>' + params[3].seriesName + ':' + params[3].value;

                            return res;
                        }
                    },
                    legend: {
                        data:['大周期ma','中周期ma','小周期ma']
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
                dataZoom : {
                    show : true,
                    realtime: true,
                    start : 0,
                    end : 0.5
                },
                xAxis : [
                    {
                        type : 'category',
                        boundaryGap : true,
                        axisTick: {onGap:false},
                        splitLine: {show:false},
                        data : [
                            <<!!xAxis>>
                        ]
                    }
                ],
                yAxis : [
                    {
                        type : 'value',
                        scale:true,
                        boundaryGap: [0.01, 0.01]
                    }
                ],
                series :
                        <<!!series>>

                };

                // 为echarts对象加载数据
                myChart.setOption(option);
            }
        );
    </script>
</body>
"""

# print template


import json
import re

def parse_date(date):
    m = re.findall("(\d{4})/(\d{2})/(\d{2})-(\d{2}):(\d{2})",date)
    if m:
        return [int(d) for d in m[0]]
    return []

def read_kdata(contract, year):
    datas = []
    filename = "data/%sL0.txt" % contract
    f = open(filename, 'r')
    if f:
        line = f.readline()
        while line:
            eles = line.split('\t')
            date = parse_date(eles[0])
            if date[0] not in year:
                break

            datas.append([eles[0], float(eles[1]), float(eles[4]), float(eles[3]), float(eles[2])])
            line = f.readline()
        f.close()
    return datas

def read_ma(contract):
    datas = [[-1],[-1],[-1]]
    filename = "log/2017-10/%s/%s/%s_hl123_ma.log" % (contract, contract, contract)
    f = open(filename, 'r')
    if f:
        line = f.readline()
        while line:
            eles = line.split('\t')
            ma1 = float(eles[2])
            ma2 = float(eles[3])
            ma3 = float(eles[4])

            datas[0].append(ma1)
            datas[1].append(ma2)
            datas[2].append(ma3)
            line = f.readline()
        f.close()

    def fill_default(datas):
        idx = len(datas)
        first_data = -1
        for data in datas[::-1]:
            if data != -1:
                first_data = data

            if data == -1:
                datas[idx-1] = first_data
            idx = idx - 1

    fill_default(datas[0])
    fill_default(datas[1])
    fill_default(datas[2])
    return datas


def read_point(contract):

    def make_time_format(time):
        return "20%02d/%02d/%02d-%02d:%02d" % (time/100000000, time/1000000%100, time/10000%100,time/100%100, time%100)

    datas = [[],[],[]]
    filename = "log/2017-10/%s/%s/%s_hl123_point123.log" % (contract, contract, contract)
    f = open(filename, 'r')
    if f:
        line = f.readline()
        while line:
            eles = line.replace('\n', '').split('\t')

            period = int(eles[0])
            time = int(eles[1])
            y = float(eles[2])
            value = eles[3]

            datas[period-1].append({'value' : value, 'xAxis': make_time_format(time), 'yAxis': y})

            line = f.readline()
        f.close()
    return datas


def main():
    year = [2010]
    contract = 'rb'

    markers = read_point(contract)

    datas = read_kdata(contract, year)
    dates = ["'" +e[0] + "'" for e in datas]
    kdatas = [[e[1],e[2],e[3],e[4]] for e in datas]

    datesstr = (',').join(dates)
    content = template.replace('<<!!xAxis>>', datesstr)

    series_k = {'name':'%s 1min' % contract,
                'type':'k',
                'data':kdatas}

    ma_group = read_ma(contract)
    series_ma1 = {'name':'大周期ma',
                'type':'line',
                'symbolSize' : '0',
                'data':ma_group[0],
                'markPoint' : {'data' : markers[0]}
                }

    series_ma2 = {'name':'中周期ma',
                'type':'line',
                'symbolSize' : '0',
                'data':ma_group[1],
                'markPoint' : {'data' : markers[1]}
                }

    series_ma3 = {'name':'小周期ma',
                'type':'line',
                'symbolSize' : '0',
                'data':ma_group[2],
                'markPoint' : {'data' : markers[2]}
                }

    series = [series_k, series_ma1, series_ma2, series_ma3]
    content = content.replace('<<!!series>>', json.dumps(series))

    f = open(u"123策略.htm", "w+")
    if f:
        f.write(content)
        f.close()

if __name__ == '__main__':
    main()
