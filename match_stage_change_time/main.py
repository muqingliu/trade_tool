import os
import re
import time
import pandas as pd
import numpy as np

def parse_datas_dir():
    paths = {}

    for parent,dirnames,filenames in os.walk('datas'):
        for filename in filenames:
            symbol = parent[parent.rindex('\\')+1:]
            if not paths.has_key(symbol): paths[symbol] = []
            paths[symbol].append(os.path.join(parent,filename))

    return paths

def load_file(path):
    names = ['date','open','high','low','close','volume']
    d = pd.read_csv(path, index_col = 0, names=names, header=None, delim_whitespace=True)

    return d


def get_period_data(datas, date, price):
    for p in datas.keys():
        if p == 'L0': continue
        if date not in datas[p].index: continue
        if price == datas[p].ix[date]['close']:
            return p
    return 0

def parse_date(date):
    m = re.match(r'(\d+)/(\d+)/(\d+)-(\d+):(\d+)', date)
    yy, MM, dd, hh, mm = [int(e) for e in m.groups()]
    return yy*10000+MM*100+dd

def calc_matched_degree(datas, idx, max_len):
    key = datas['L0'].ix[idx].name
    first_date = parse_date(key)

    symbols = datas.keys()
    symbols.remove('L0')
    matched_counter = {s:0 for s in symbols}

    looptimes = max(min(500, max_len - idx - 1), 0)
    if looptimes == 0: return 0,0

    for x in xrange(0,looptimes):
        key = datas['L0'].ix[idx+x].name
        date = parse_date(key)

        if date != first_date: break # 跨天了，退出循环
        for symbol in symbols:
            if key in datas[symbol].index:
                if datas[symbol].ix[key]['close'] == datas['L0'].ix[key]['close']:
                    matched_counter[symbol] += 1

    r = sorted(matched_counter.iteritems(), key= lambda d:d[1], reverse = True)
    return r[0][0], x


def process_symbol(symbol, paths):

    datas = {}

    for path in paths:
        ds = load_file(path)
        period = path[-6:-4].upper()
        datas[period] = ds

    cur_period = 0
    error_count = 0

    max_len = len(datas['L0'])
    i = 0
    last_i = 0
    result = []
    start = time.time()
    while i < max_len:
        period, number = calc_matched_degree(datas, i, max_len)

        if period == 0 or number == 0: break

        date = datas['L0'].ix[i].name

        if cur_period != period:
            flag = [date, period]
            result.append(flag)
            print flag
            end = time.time()
            print 'time elapse: %.4f, index:%d/%d/%d' % (end-start, i-last_i, i, max_len)
            last_i = i
            start = time.time()


        cur_period = period
        error_count = 0
        i += number
    end = time.time()
    print 'time elapse: %.4f' % (end-start)

    f = open(r'datas\%s\result.txt' %(symbol), 'w+')
    if f:
        for t, period in result:
            f.write("%s\t%s\n" % (t, period))
        f.close()

def main():
    paths = parse_datas_dir()

    for symbol, path in paths.items():
        process_symbol(symbol, path)


if __name__ == '__main__':
    main()
