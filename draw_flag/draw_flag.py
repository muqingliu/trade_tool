year = [2010,2011,2012,2013,2014,2015,2016,2017,2018]
contract = 'rb'
# LOG_PATH = "log/2017-11/%s/%s/" % (contract, contract)
LOG_PATH = ""#"log/2017-11/%s/" % (contract)
class CONST():
    P_TYPE_H = 1
    P_TYPE_L = 2

template ="""
<!DOCTYPE html>
<head>
    <meta charset="utf-8">
    <title>9笔策略</title>
</head>
<body>
    <!-- 为ECharts准备一个具备大小（宽高）的Dom -->
    <div id="main" style="height:800px"></div>
    <!-- ECharts单文件引入 -->
    <script src="echarts.js"></script>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts图表
        var myChart = echarts.init(document.getElementById('main'));

        var mp_buy = {"normal":{"color": "rgb(150,0,0)", "label": {"formatter":
        function(param){
            var type = Math.floor(param.value/10)
            var desc = param.value%10
            var lable = "开仓";
            if(type == 1) lable = "平仓";
            if(desc == 1) lable= "止盈";
            if(desc == 2) lable= "止损";
            return lable;
        }}}};
        var mp_sell = {"normal":{"color": "rgb(0,150,0)", "label": {"formatter":
        function(param){
            var type = Math.floor(param.value/10)
            var desc = param.value%10
            var lable = "开仓";
            if(type == 1) lable = "平仓";
            if(desc == 1) lable= "止盈";
            if(desc == 2) lable= "止损";
            return lable;
        }}}};

        var option = {
             tooltip : {
                trigger: 'axis',
                axisPointer: {
                   type: 'cross'
                }
            },
            legend: {
                data:['ma5','ma10','ma25','ma50','line_s','line_m']
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
            //type: 'inside',
            //xAxisIndex: [0, 1],
            //show : true,
            //realtime: true,
            //start : 0,
            //end :20
            {
                type: 'inside',
                //xAxisIndex: [0, 1],
                start: 0,
                end: 2
            },
            {
                show: true,
                //xAxisIndex: [0, 1],
                type: 'slider',
                top: '85%',
                start: 0,
                end: 2
            }
        ],
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
    </script>
</body>
"""

# print template
import json
import re
import os

def parse_date(date):
    m = re.findall("(\d{4})/(\d{2})/(\d{2})-(\d{2}):(\d{2})",date)
    if m:
        return [int(d) for d in m[0]]
    return []

def make_date(date):
    return '20%s/%s/%s-%s:%s' % (date[0:2], date[2:4], date[4:6], date[6:8], date[8:10])

def read_kdata(contract, year):
    datas = []
    filename = "data/%sL0.txt" % contract
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            eles = line.split('\t')
            date_str = make_date(eles[0])
            date = parse_date(date_str)
            if date[0] in year:
                # print eles
                datas.append([eles[0], float(eles[1]), float(eles[4]), float(eles[3]), float(eles[2])])
            line = f.readline()
    return datas

def read_ma(contract):
    dirs = []
    datas = [[],[],[],[],[]]
    filename = os.path.join(LOG_PATH, "%s_hl9_ma.log" % (contract))
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            eles = line.replace('\n', '').split('\t')
            dt  = eles[0]
            ma1 = float(eles[2])
            ma2 = float(eles[3])
            ma3 = float(eles[4])
            ma4 = float(eles[5])
            pdir= eles[7]
            dirs.append([dt, pdir])

            datas[0].append(ma1)
            datas[1].append(ma2)
            datas[2].append(ma3)
            datas[3].append(ma4)
            line = f.readline()

    def fill_default(datas):
        idx = len(datas)
        first_data = -1
        for data in datas[::-1]:
            if data != -1:
                first_data = data

            if data == -1:
                datas[idx-1] = first_data
                datas[idx-1] = '-'
            idx = idx - 1

    fill_default(datas[0])
    fill_default(datas[1])
    fill_default(datas[2])
    fill_default(datas[3])
    return datas, dirs

def read_policy(contract):
    datas = []
    filename = os.path.join(LOG_PATH, "%s_ma_test_policy.log" % (contract))
    with open(filename, 'r') as f:
        line = f.readline()
        line_index = 1
        while line:            
            # if line.decode('gbk').find(u'类型') == -1:
            #     line = f.readline()
            #     line_index = line_index + 1
            #     continue
            trade_type  = 0
            trade_dir   = 0
            time        = 0
            num         = 0
            price       = 0
            equity      = 0
            desc        = 0
            ma = re.search('\s([^\[]+)', line.replace('\n', '').decode('gbk'))
            if ma:
                trade_type = 0 if ma.group(1) == u'开' else 1
            else:
                print 'parse error[1] line %d' % line_index

            ma = re.findall('\[([^\]]+)\]', line.replace('\n', '').decode('gbk'))
            if ma:
                time        = ma[0]
                num         = ma[1]
                price       = ma[3]
                equity      = ma[4]
                trade_dir   = 0 if ma[2] == u'多' else 1
                desc        = ma[5] if len(ma) == 6 else 0
            else:
                print 'parse error[2] line %d' % line_index

            datas.append([time, trade_type, num, trade_dir, price, equity, desc])

            line = f.readline()
            line_index = line_index + 1
    return datas

def make_policy_markpoint(policys):
    datas = []
    dg = {u'开仓': 0, u'止盈': 1, u'止损': 2, 0 : 9}
    for p in policys:
        trade_type = int(p[1])
        trade_dir = int(p[3])
        desctype = dg[p[6]]

        itemStyle = 'mp_buy' if trade_dir == 0 else 'mp_sell'
        if trade_type == 1: itemStyle = 'mp_sell' if trade_dir == 0 else 'mp_buy'

        ele = {'symbolRotate': 0 if trade_type == 0 else 180,'value' : trade_type*10+desctype, 'xAxis': make_date(p[0]), 'yAxis': p[4],'itemStyle': itemStyle}
        datas.append(ele)
    return datas

#读取高低点信息
def read_high_low(contract):
    filename = os.path.join(LOG_PATH, "%s_ma_test_high_low.log" % (contract))
    datas = {CONST.P_TYPE_H: [], CONST.P_TYPE_L : []}
    with open(filename, "rb") as fp:
        line = fp.readline()
        while line:
            eles = line.split('\t')
            if eles[0] == 'high':
                datas[CONST.P_TYPE_H].append([eles[2], float(eles[3])])
            elif eles[0] == 'low':
                datas[CONST.P_TYPE_L].append([eles[2], float(eles[3])])

            line = fp.readline()
    return datas

def read_results(contract):
    datas = []
    filename = os.path.join(LOG_PATH, "%s_result.txt" % (contract))
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            eles = line.replace('\n', '').split('\t')
            if len(eles) < 8:
                line = f.readline()
                continue

            time1 = eles[0]
            price1 = float(eles[1])
            time2 = eles[2]
            price2 = float(eles[3])
            time3 = eles[4]
            price3 = float(eles[5])
            time4 = eles[6]
            price4 = float(eles[7])

            line_pair1 = [[time1, price1], [time2, price2]]
            line_pair2 = [[time3, price3], [time4, price4]]

            datas.append(line_pair1)
            datas.append(line_pair2)

            line = f.readline()
    return datas

def read_line_s():
    filename = os.path.join(LOG_PATH, "%s_hl9_point.log" % (contract))
    datas = {CONST.P_TYPE_L: [], CONST.P_TYPE_M : [], CONST.P_TYPE_S: []}
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            eles = line.replace('\n', '').split('\t')
            if len(eles) < 3:
                line = f.readline()
                continue

            time = make_date(eles[0])
            period  = int(eles[1])
            pt   = float(eles[2])
            dir  = int(eles[3])

            datas[period].append([time, pt])

            line = f.readline()
    return datas

def main():

    datas = read_kdata(contract, year)
    dates = ["'" +e[0] + "'" for e in datas]
    kdatas = [[e[1],e[2],e[3],e[4]] for e in datas]

    datesstr = (',').join(dates[1:])
    content = template.replace('<<!!xAxis>>', datesstr)

    #policys = read_policy(contract)
    #mp = make_policy_markpoint(policys)

    series_k = {'name':'%s 1min' % contract,
                'type':'k',
                'data':kdatas[:],
                }

    #ma_group, dirs = read_ma(contract)

    # dir_begin = 0
    # dir_end = 0
    # dir_type = -1
    # markAreaData = []
    # for dt, pdir in dirs:
    #     if dir_type != pdir:
    #         if dir_begin > 0 and dir_end > 0 and dir_type != '0':
    #             style =  {'normal': {'color': 'rgb(0,150,200)'}}
    #             if dir_type == '1':
    #                 style =  {'normal': {'color': 'rgb(150,0,200)'}}
    #             markAreaData.append([{'itemStyle':style,'xAxis':make_date(str(dir_begin))},{'xAxis':make_date(str(dir_end))}])
    #         dir_begin = dt
    #         dir_type = pdir
    #     else:
    #         dir_end = dt


    # series_ma1 = {'name':'ma5',
    #             'type':'line',
    #             'symbolSize' : '0',
    #             'itemStyle': {'normal': {'color': 'rgb(0,150,200)'}},
    #             'data':ma_group[0][:],
    #             # 'markArea': { 'data': markAreaData }
    #             }

    # series_ma2 = {'name':'ma10',
    #             'type':'line',
    #             'symbolSize' : '0',
    #             'data':ma_group[1][:],
    #             }

    # series_ma3 = {'name':'ma25',
    #             'type':'line',
    #             'symbolSize' : '0',
    #             'data':ma_group[2][:],
    #             }

    # series_ma4 = {'name':'ma50',
    #             'type':'line',
    #             'symbolSize' : '0',
    #             'data':ma_group[3][:],
    #             }

    # high_low_datas = read_high_low(contract)

    # series_line_h ={'name': 'line_h',
    #              'type': 'line',
    #              'data': high_low_datas[CONST.P_TYPE_H][:]
    #             }

    # series_line_l ={'name': 'line_l',
    #              'type': 'line',
    #              'data': high_low_datas[CONST.P_TYPE_L][:]
    #             }

    result_lines = read_results(contract)
    print result_lines
    result_size = len(result_lines)

    series = [series_k]
    for i in xrange(0,result_size):
        name = "resist_line_%u" % i
        series_line ={'name': name,
                        'type': 'line',
                        'data': result_lines[i]
                    }
        series.append(series_line)


    # series = [series_k, series_ma1, series_ma2, series_ma3, series_ma4, series_line_s, series_line_m]

    # series = [series_line_s]
    content = content.replace('<<!!series>>', json.dumps(series))
    content = content.replace('"mp_buy"', 'mp_buy')
    content = content.replace('"mp_sell"', 'mp_sell')

    f = open(u"9笔策略.htm", "w+")
    if f:
        f.write(content)
        f.close()

if __name__ == '__main__':
    main()
