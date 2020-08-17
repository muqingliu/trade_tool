year_set = [2010,2011,2012,2013,2014,2015,2016,2017,2018]


template ="""
<!DOCTYPE html>
<head>
    <meta charset="utf-8">
    <title><<!!title>></title>
</head>
<body>
    <!-- 为ECharts准备一个具备大小（宽高）的Dom -->
    <<!!div_set>>
    <div id="main_total" style=\"height:400px\"></div>
    <!-- ECharts单文件引入 -->
    <script src="echarts.js"></script>
    <script src="common_echart.js"></script>
    <script type="text/javascript">
        var mp_buy = {
            "normal": {
                "color": "rgb(150,0,0)", 
                "label": {
                    "show":false,
                    "formatter": function(param) {
                        var type = Math.floor(param.value/10)
                        var desc = param.value%10
                        var lable = "开仓";
                        if(type == 1) lable = "平仓";
                        if(desc == 1) lable= "止盈";
                        if(desc == 2) lable= "止损";
                        return lable;
                    }
                }
            }
        };
        var mp_sell = {
            "normal": {
                "color": "rgb(0,150,0)", 
                "label": {
                    "show":false,
                    "formatter": function(param) {
                        var type = Math.floor(param.value/10)
                        var desc = param.value%10
                        var lable = "开仓";
                        if(type == 1) lable = "平仓";
                        if(desc == 1) lable= "止盈";
                        if(desc == 2) lable= "止损";
                        return lable;
                    }
                }
            }
        };

        <<!!year_chart>>
        <<!!total_chart>>
    </script>
</body>
"""


import json
import re
import os
import time


def find_test_result_file(rootdir):
    test_tool_dirs = [rootdir]
    # for parent,dirnames,filenames in os.walk(rootdir):
    #     if parent == rootdir:
    #         test_tool_dirs.extend(dirnames)

    map_test_file = {}

    map_contract_tr_full_path = {}
    map_contract_log_full_path = {}
    for test_tool_dir in test_tool_dirs:
        test_tool_full_path = os.path.join(rootdir,test_tool_dir)
        test_log_full_path = "%s\\log" % (test_tool_full_path)

        tar_dir = ""
        max_number = 0
        for parent,dirnames,filenames in os.walk(test_log_full_path):
            if parent == test_log_full_path:
                for dirname in dirnames:
                    number = int(dirname.replace("-", ""))
                    if number > max_number:
                        max_number = number
                        tar_dir = dirname

        test_log_full_path = os.path.join(test_log_full_path, tar_dir)

        for parent,dirnames,filenames in os.walk(test_log_full_path):
            for dirname in dirnames:
                contract = dirname
                contract_log_full_path = "%s\\%s\\%s" % (test_log_full_path, contract, contract)
                map_contract_log_full_path[contract] = contract_log_full_path

        test_db_full_path = "%s\\db" % (test_tool_full_path)
        for parent,dirnames,filenames in os.walk(test_db_full_path):
            for dirname in dirnames:
                contract = dirname
                contract_tr_full_path = "%s\\%s\\trade_records.db" % (test_db_full_path, contract)
                if not map_test_file.has_key(contract):
                    map_test_file[contract] = {}

                map_test_file[contract]["trade_records"] = contract_tr_full_path

    for contract in map_contract_log_full_path.keys():
        contract_log_full_path = map_contract_log_full_path[contract]
        for parent,dirnames,filenames in os.walk(contract_log_full_path):
            if not map_test_file.has_key(contract):
                map_test_file[contract] = {}

            for filename in filenames:
                file_word_list = filename.split('_')
                if filename.find("margin") >= 0 and file_word_list[0] != contract:
                    full_file_path = os.path.join(parent,filename)
                    map_test_file[contract]["margin"] = full_file_path

                if filename.find("high_low") >= 0:
                    full_file_path = os.path.join(parent,filename)
                    map_test_file[contract]["high_low"] = full_file_path

    return map_test_file


def get_web_path(rootdir, policy, contract):
    full_path = os.path.join(rootdir,policy)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    full_path = "%s\\%s.htm" % (full_path, contract)
    return full_path


def parse_time(time):
    m = re.findall("(\d{4})/(\d{2})/(\d{2})-(\d{2}):(\d{2})",time)
    if m:
        return [int(d) for d in m[0]]
    return []


def parse_margin_time(time):
    time_set = []
    m = re.findall("(\d{6})-(\d{2}):(\d{2})",time)
    if m:
        arrs = m.groups()
        year = 2000 + int(arrs[0]) / 10000
        month = int(arrs[0]) / 100 % 100
        day = int(arrs[0]) % 100
        hour = 9
        minute = 1
        time_set.append(year)
        time_set.append(month)
        time_set.append(day)
        time_set.append(hour)
        time_set.append(minute)
    return time_set
    

def make_time(time):
    return '20%s/%s/%s-%s:%s' % (time[0:2], time[2:4], time[4:6], time[6:8], time[8:10])


def make_margin_time(time):
    m = re.findall("(\d{6})-(\d{2}):(\d{2})",time)
    if m:
        arrs = m[0]
        result = '20%s/%s/%s-15:00' % (arrs[0][0:2], arrs[0][2:4], arrs[0][4:6])
        return result
    return ""


def read_kdata(contract, year):
    datas = []
    filename = "data/%sL0.txt" % contract
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            eles = line.split('\t')
            time = parse_time(eles[0])
            if time[0] == year:
                datas.append([eles[0], float(eles[1]), float(eles[4]), float(eles[3]), float(eles[2])])

            line = f.readline()
    return datas


def read_trade_record(tar_contract, filename):
    datas = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            equity      = 0
            desc        = 0
            tr_info = line.decode('gbk').split('\t')
            yymmdd              = tr_info[0][2:]
            list_hhmmss         = tr_info[1].split(':')
            time                = "%s%s%s" % (yymmdd,list_hhmmss[0],list_hhmmss[1])
            contract            = tr_info[2]
            trade_dir           = 0 if tr_info[3] == u"买入" else 1
            trade_type          = 0 if tr_info[4] == u"开仓" else 1
            price               = float(tr_info[5])
            num                 = int(tr_info[6])

            if tar_contract == contract:
                datas.append([time, trade_type, num, trade_dir, price, equity, desc])

            line = f.readline()

    return datas


def read_high_low(filename):
    datas = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            tr_info = line.split('\t')
            type_str            = tr_info[0]
            time                = tr_info[3]
            price               = float(tr_info[4])

            datas.append([type_str, time, price])

            line = f.readline()

    return datas


def read_margin(filename):
    init_money = 0
    datas = [[],[],[],[],[],[],[]]
    with open(filename, 'rb') as f:
        line = f.readline()
        while line:
            eles = line.split('\t')
            time = make_margin_time(eles[0])
            profit = float(eles[1])
            equity = float(eles[2])
            margin = int(round(float(eles[3])))
            margin_rate = float("%.4f" % float(eles[4]))
            retract_money = int(round(float(eles[5])))
            retract = float("%.4f" % float(eles[6]))

            if init_money == 0:
                init_money = profit + equity

            datas[0].append(time)
            datas[1].append([time, profit])
            datas[2].append([time, equity])
            datas[3].append([time, margin])
            datas[4].append([time, margin_rate])
            datas[5].append([time, -retract_money])
            datas[6].append([time, -retract])
            line = f.readline()

    return (init_money, datas)


def make_policy_markpoint(policys):
    datas = []
    dg = {u'开仓': 0, u'止盈': 1, u'止损': 2, 0 : 9}
    for p in policys:
        trade_type = int(p[1])
        trade_dir = int(p[3])
        desctype = dg[p[6]]

        itemStyle = 'mp_buy' if trade_dir == 0 else 'mp_sell'
        #if trade_type == 1: itemStyle = 'mp_sell' if trade_dir == 0 else 'mp_buy'

        #tooltip = u"时间[%s] %s %s 价格:%s 数量:%s" % (make_date(p[0]), trade_type_str, trade_dir_str, p[4], p[2])

        ele = {'symbolRotate': 0 if trade_type == 0 else 180,'value' : trade_type*10+desctype, 'xAxis': make_time(p[0]), 
                'yAxis': p[4],'itemStyle': itemStyle}
        datas.append(ele)

    return datas


def make_high_low_makepoint(high_low_points):
    datas = []
    for p in high_low_points:
        itemStyle = 'mp_buy' if p[0] == "high" else 'mp_sell'
        ele = {'symbolRotate':0,'value':0,'xAxis':make_time(p[1]),'yAxis':p[2],'itemStyle':itemStyle}
        datas.append(ele)

    return datas


def create_div_str(year):
    div_str = "<div id=\"main_%u\" style=\"height:700px\"></div>\n" % year
    return div_str


def create_chart_str(contract, year, mp, datas_margin):
    datas = read_kdata(contract, year)
    if len(datas) == 0:
        return ""

    title = "%s_%u" % (contract, year)
    div_name = "main_%u" % year

    times = ["'" +e[0] + "'" for e in datas]
    kdatas = [e[4] for e in datas]

    begin_idx = 0
    end_idx = -1

    timesstr = (',').join(times[begin_idx:end_idx])

    series_k = {'name':'%s 1min' % contract,
                'type':'line',
                'xAxisIndex' : 0,
                'yAxisIndex' : 0,
                'data':kdatas[begin_idx:end_idx],
                'markPoint' : {'data' : mp,
                    'symbolSize' : 20
                }
                }

    series_profit = {'name':'利润',
                'type':'line',
                'xAxisIndex' : 0,
                'yAxisIndex' : 1,
                'data':datas_margin[1][0:]
                }

    series_margin = {'name':'保证金',
                'type':'line',
                'xAxisIndex' : 1,
                'yAxisIndex' : 2,
                'data':datas_margin[3][0:]
                }

    series_retrace_money = {'name':'回撤值',
                'type':'line',
                'xAxisIndex' : 1,
                'yAxisIndex' : 2,
                'data':datas_margin[5][0:]
                }

    series_margin_rate = {'name':'保证金率',
                'type':'bar',
                'xAxisIndex' : 1,
                'yAxisIndex' : 3,
                'barWidth' :10,
                'data':datas_margin[4][0:]
                }

    series_retrace = {'name':'回撤',
                'type':'bar',
                'xAxisIndex' : 1,
                'yAxisIndex' : 3,
                'barWidth' :10,
                'data':datas_margin[6][0:]
                }

    series = [series_k,series_profit,series_margin,series_retrace_money,series_margin_rate,series_retrace]
    series_names_str = (',').join(["'" + serie['name'] + "'" for serie in series])

    chart_str = "chart_draw_four_y_axis(echarts, \"%s\", \"%s\", [\"价格\",\"利润\",\"值\",\"率\"], [%s], [%s], %s);\n" \
                % (div_name, title, series_names_str, timesstr, json.dumps(series))
    return chart_str


def create_total_chart_str(contract, init_money, datas_margin):
    title = "%s_%u" % (contract, init_money)

    timesstr = (',').join(["'%s'" % time for time in datas_margin[0]])

    series_profit = {'name':'利润',
                'type':'line',
                'data':datas_margin[1][0:]
                }

    series_retrace_money = {'name':'回撤值',
                'type':'line',
                'data':datas_margin[5][0:]
                }

    series_margin = {'name':'保证金',
                'type':'bar',
                'yAxisIndex' : 1,
                'data':datas_margin[3][0:]
                }

    series = [series_profit,series_retrace_money,series_margin]
    chart_str = "chart_draw_two_line_bar(echarts, \"main_total\", \"%s\", [\"利润和回撤\",\"保证金\"], [\"利润\",\"回撤值\",\"保证金\"], "\
                "[%s], %s);\n" % (title, timesstr, json.dumps(series))
    return chart_str


def create_result_web(contract, margin_file, trade_record_file):
    policys = read_trade_record(contract, trade_record_file)
    mp = make_policy_markpoint(policys[0:])
    # high_low_points = read_high_low(trade_record_file)
    # mp = make_high_low_makepoint(high_low_points[0:])

    margin_info = read_margin(margin_file)
    init_money = margin_info[0]
    datas_margin = margin_info[1]

    div_str = ""
    chart_str = ""
    for year in year_set:
        chart_str_year = create_chart_str(contract, year, mp, datas_margin)
        if len(chart_str_year) == 0:
            continue

        div_str_year = create_div_str(year)

        div_str += div_str_year
        chart_str += chart_str_year

    total_chart_str = create_total_chart_str(contract, init_money, datas_margin)

    content = template.replace('<<!!title>>', contract)
    content = content.replace('<<!!div_set>>', div_str)
    content = content.replace('<<!!year_chart>>', chart_str)
    content = content.replace('<<!!total_chart>>', total_chart_str)
    content = content.replace('"mp_buy"', 'mp_buy')
    content = content.replace('"mp_sell"', 'mp_sell')

    f = open("%s.htm" % contract, "w+")
    if f:
        f.write(content)
        f.close()


def main():
    cur_path = os.getcwd()
    map_test_file = find_test_result_file(cur_path)
    for contract in map_test_file:
        test_result_files = map_test_file[contract]
        if len(test_result_files) == 0:
            continue

        print contract
        create_result_web(contract, test_result_files["margin"], test_result_files["trade_records"])


if __name__ == '__main__':
    main()
