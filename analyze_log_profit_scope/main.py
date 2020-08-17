
# 日志路径
g_log_dir = r'N:\Project\trader\bin\TradeTool\log\2017-6'


####################################################################################
import os
import pandas as pd
import numpy as np


def load_datas(symbol):
    names = ['date','open','high','low','close','volume']

    d = pd.read_csv(r'datas\%sL0.txt' % symbol, index_col = 0, names=names, header=None, delim_whitespace=True)
    return d


def parse_logs_dir():
    symbols =[]
    paths = []

    for parent,dirnames,filenames in os.walk(g_log_dir):
         for dirname in  dirnames:
              symbols.append(dirname)

         for filename in filenames:
            if filename.find('lots_profit.log') >=0:
                paths.append([parent[parent.rindex('\\')+1:], os.path.join(parent,filename)])

    return symbols, paths


def get_closedata_from_time(datas, symbol, time):
    yy = time / 100000000
    MM = time / 1000000 % 100
    dd = time / 10000 % 100
    hh = time / 100 % 100
    mm = time % 100

    key ='20%d/%02d/%02d-%02d:%02d' % (yy, MM, dd, hh, mm)
    return datas[symbol].ix[key]['close']


def parse_log(log_name):
    '''读取策略生成的每笔交易利润统计日志'''
    f = open(log_name, 'rt')
    if not f: return

    points_data = []
    l = f.readline()
    while l:
        # try:
        els = l.split('\t')
        time_open = int(els[4])
        time_close = els[0]
        ever_point = float(els[5])
        trade_times = int(els[6].replace('\n', ''))
        points_data.append([time_open, time_close, ever_point, trade_times])

        l = f.readline()
    f.close()

    return points_data

def save_log(log_name, datas):
    f = open(log_name, 'w+')
    if f:
        for data in datas:
            f.write(('\t').join(str(s) for s in data) + '\n')
        f.close()

def main():
    symbols, paths = parse_logs_dir()
    datas = {s: load_datas(s) for s in symbols}

    for symbol, log_file in paths:
        points_data = parse_log(log_file)

        results = []
        for time_open, time_close, ever_point, trade_times in points_data:

            # 从连续数据中查找该时间的收盘价
            close_price = get_closedata_from_time(datas, symbol, time_open)
            ratio = ever_point / close_price
            results.append([time_close, ever_point, trade_times, ratio])

        save_log("%s/profit_ratio.log" % os.path.dirname(log_file), results)


if __name__ == '__main__':
    main()

