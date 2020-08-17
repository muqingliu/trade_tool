#-*- coding: UTF-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

year_set = [2010,2011,2012,2013,2014,2015,2016,2017,2018]

template = """
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
import db
import time
import datetime
import exchange_config


db_host = "www.5656k.com"
db_user = "stock"
db_pwd  = "P)O(I*U&Y^"
db_dbase= "stock_realtime"
db_port = 3308


def get_symbol(contract):
    ma = re.search("([A-Za-z]+)(\d+)", contract)
    if ma:
        arrs = ma.groups()
        symbol = arrs[0]
        return symbol
    return ""


def parse_time(time):
    m = re.findall("(\d{4})/(\d{2})/(\d{2})-(\d{2}):(\d{2})",time)
    if m:
        return [int(d) for d in m[0]]
    return []


def make_time(time):
    return '20%s/%s/%s-%s:%s' % (time[0:2], time[2:4], time[4:6], time[6:8], time[8:10])


def read_real_kdata(db, exg_cfg, contract, begin_yymm):
    symbol = get_symbol(contract)
    exchange = exg_cfg.get_contract_exchage(symbol)
    table = "hq_%s_k1" % exchange
    sql = "select * from %s where InstrumentID='%s' and Time>=%u and Time<=%u" % (table, contract, begin_yymm*1000000, 
        (begin_yymm/100+1)*100000000)
    db.Query(sql)
    recs = db.FetchAll()
    klines = []
    if recs and len(recs) > 0:
        for rec in recs:
            kline = [rec[2],float(rec[3]),float(rec[5]),float(rec[6]),float(rec[4])]
            klines.append(kline)
            
    return klines


def modify_real_tr_date(tr_datas):
    for tr in list_tr:
        yyyymmdd = int(tr[0])
        list_hhmmss = tr[1].split(':')
        hh = int(list_hhmmss[0])
        mm = int(list_hhmmss[1])
        ss = int(list_hhmmss[2])

        st_date = datetime.date(yyyymmdd / 10000, yyyymmdd / 100 % 100, yyyymmdd % 100)
        st_time = datetime.time(hh, mm, ss)

        if hh >= 20:
            if st_date.isoweekday() == 1:
                st_date = st_date - datetime.timedelta(days = 3)
            else:
                st_date = st_date - datetime.timedelta(days = 1)
        elif hh >= 0 and hh <= 3:
            if st_date.isoweekday() == 1:
                st_date = st_date - datetime.timedelta(days = 2)

        date_str_new = "%04u%02u%02u" % (st_date.year,st_date.month,st_date.day)
        f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (date_str_new,tr[1],tr[2],tr[3],tr[4],tr[5],tr[6],tr[7],tr[8],tr[9]))


def read_real_trade_record(filename):
    contracts_datas = {}
    with open(filename, 'r') as f:
        line = f.readline()
        line_index = 1
        while line:
            equity      = 0
            desc        = 0
            tr_info = line.decode('gbk').split('\t')
            yyyymmdd_str        = tr_info[0]
            list_hhmmss_str     = tr_info[1].split(':')
            contract            = tr_info[2]
            trade_dir           = 0 if tr_info[3] == u"买入" else 1
            trade_type          = 0 if tr_info[4] == u"开仓" else 1
            price               = float(tr_info[5])
            num                 = int(tr_info[6])

            yyyymmdd = int(yyyymmdd_str)
            st_date = datetime.date(yyyymmdd / 10000, yyyymmdd / 100 % 100, yyyymmdd % 100)
            st_time = datetime.datetime(yyyymmdd / 10000, yyyymmdd / 100 % 100, yyyymmdd % 100, int(list_hhmmss_str[0]), 
                int(list_hhmmss_str[1]), int(list_hhmmss_str[2]))

            #为了对应分钟线时间戳，交易记录夜盘日期应该转为真实日期
            if st_time.hour >= 20:
                if st_date.isoweekday() == 1:
                    st_date = st_date - datetime.timedelta(days = 3)
                else:
                    st_date = st_date - datetime.timedelta(days = 1)
            elif st_time.hour >= 0 and st_time.hour <= 3:
                if st_date.isoweekday() == 1:
                    st_date = st_date - datetime.timedelta(days = 2)
            #为了对应分钟线时间戳，交易记录时间戳应往后挪一分钟
            st_time = st_time + datetime.timedelta(minutes = 1)

            time = "%02u%02u%02u%02u%02u" % (st_date.year%100,st_date.month,st_date.day,st_time.hour,st_time.minute)

            if not contracts_datas.has_key(contract):
                contracts_datas[contract] = []

            contracts_datas[contract].append([time, trade_type, num, trade_dir, price, equity, desc])

            line = f.readline()
            line_index = line_index + 1

    return contracts_datas    


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


def create_div_str(year):
    div_str = "<div id=\"main_%u\" style=\"height:700px\"></div>\n" % year
    return div_str


def create_real_chart_str(contract, year, mp, datas):
    if len(datas) == 0:
        return ""

    title = "%s_%u" % (contract, year)
    div_name = "main_%u" % year

    times = ["'" + make_time("%u"%e[0]) + "'" for e in datas]
    kdatas = [[e[1],e[2],e[3],e[4]] for e in datas]

    begin_idx = 1
    end_idx = -1

    timesstr = (',').join(times[begin_idx:end_idx])

    series_k = {'name':'%s 1min' % contract,
                'type':'k',
                'xAxisIndex' : 0,
                'yAxisIndex' : 0,
                'data':kdatas[begin_idx:end_idx],
                'markPoint' : {'data' : mp}
                }

    series = [series_k]

    chart_str = "chart_draw_k(echarts, \"%s\", \"%s\", \"价格\", [%s], %s);\n" % (div_name, title, timesstr, json.dumps(series))
    return chart_str


def create_real_result_web(db, exg_cfg, contract, tr_datas):
    mp = make_policy_markpoint(tr_datas)
    begin_year = 2000 + int(tr_datas[0][0]) / 100000000
    begin_yymm = int(tr_datas[0][0]) / 1000000
    div_str = ""
    chart_str = ""
    for year in year_set:
        if year < begin_year:
            continue

        yymm = begin_yymm
        if year > 2000 + begin_yymm / 100:
            yymm = year % 100 * 100

        kdatas = read_real_kdata(db, exg_cfg, contract, yymm)
        chart_str_year = create_real_chart_str(contract, year, mp, kdatas)
        if len(chart_str_year) == 0:
            continue

        div_str_year = create_div_str(year)

        div_str += div_str_year
        chart_str += chart_str_year

    content = template.replace('<<!!title>>', contract)
    content = content.replace('<<!!div_set>>', div_str)
    content = content.replace('<<!!year_chart>>', chart_str)
    content = content.replace('<<!!total_chart>>', '')
    content = content.replace('"mp_buy"', 'mp_buy')
    content = content.replace('"mp_sell"', 'mp_sell')

    f = open("report/%s.htm" % contract, "w+")
    if f:
        f.write(content)
        f.close()


def main():
    cur_path = os.getcwd()
    if not os.path.exists(cur_path + "/report"):
        os.makedirs(cur_path+"/report") 

    exg_cfg = exchange_config.exchange_config(os.path.join(cur_path, "exchange.ini"))
    database = db.DB(host=db_host,user=db_user, passwd=db_pwd, db=db_dbase, table_name='', port=db_port)
    tr_filename = "%s\\trade_records.db" % (cur_path)
    contracts_datas = read_real_trade_record(tr_filename)
    for contract in contracts_datas.keys():
        print contract
        create_real_result_web(database, exg_cfg, contract, contracts_datas[contract])
        

if __name__ == '__main__':
    main()
