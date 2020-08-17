from common import web
from common import db
from common import log
from bs4 import BeautifulSoup
import os
import re
import basefunc
import spynner
import time,datetime


def fix_time(yymmhhmm):
    if yymmhhmm % 100 != 59:
        yymmhhmm += 1
    else:
        yymmhhmm = yymmhhmm / 100 * 100 + 100
    return yymmhhmm


def is_trade_local_time(now_time):
    hhmm = now_time%10000
    weekday = datetime.date.today().weekday()

    if weekday == 5 or weekday ==6: return False
    if hhmm >=928 and hhmm <= 1132: return True  # 怕计算时间与交易所时间不同，时间稍微留富裕些，具体内部再过滤
    if hhmm >=1258 and hhmm <= 1502: return True
    return False


def is_trade_time(time):
    hhmm = time%10000
    if hhmm >=930 and hhmm <= 1129: return True 
    if hhmm >=1259 and hhmm <= 1459: return True
    return False


class c_rec(object):
    def __init__(this):
        this.datas ={}

    def set(this, name, data):
        this.datas[name] = data

    def get(this, name):
        if this.datas.has_key(name) : return this.datas[name]
        return 0

    def count(this):
        return len(this.datas)


class c_rec_manager(object):
    def __init__(this):
        this.datas = {}
        this.time_stack = []
        this.last_time_data = {}

    def set(this, db, contract, datetime, data):
        yymmhhmm = datetime / 100
        yymmhhmm = fix_time(yymmhhmm) # 时间戳向后挪一分钟与采集的IF数据时间戳对应

        if not is_trade_time(yymmhhmm): return
        if not this.datas.has_key(yymmhhmm): rec = this.datas[yymmhhmm] = c_rec()
        else: rec = this.datas[yymmhhmm]
        rec.set(contract, data)

        log.WriteLog("%s.log" % contract, "%s\t%f" % (datetime, data))

        this._update_data_to_db(db, contract, yymmhhmm, rec.get(contract))

        if yymmhhmm not in this.time_stack: this.time_stack.append(yymmhhmm)
        if len(this.time_stack) > 10: # 删除过多的历史记录
            ready_del = this.time_stack[:len(this.time_stack) - 10]
            for d in ready_del:
                del this.datas[d]
                this.time_stack = this.time_stack[len(this.time_stack) - 10:]
    
    def _update_data_to_db(this, db, contract, datetime, price):
        if not this.last_time_data.has_key(contract):
            this.last_time_data[contract] = []

        contract_last_time_data = this.last_time_data[contract]
        if len(contract_last_time_data) > 0 and contract_last_time_data[0] == datetime:
            if price > contract_last_time_data[2]:
                contract_last_time_data[2] = price
            elif price < contract_last_time_data[3]:
                contract_last_time_data[3] = price
            contract_last_time_data[4] = price
        elif len(contract_last_time_data) == 0:
            contract_last_time_data.extend([datetime, price, price, price, price])
        elif contract_last_time_data[0] != datetime:
            contract_last_time_data[0] = datetime
            contract_last_time_data[1] = price
            contract_last_time_data[2] = price
            contract_last_time_data[3] = price
            contract_last_time_data[4] = price

        sql = "REPLACE INTO new_etf_data(`contract`,`datetime`,`open`,`high`,`low`,`close`) VALUES('%s','%d','%f','%f','%f','%f')" % (contract, 
            contract_last_time_data[0], contract_last_time_data[1], contract_last_time_data[2], contract_last_time_data[3], 
            contract_last_time_data[4])
        db.Execute(sql)


def load_contract(filename):
    contract_set = []
    with open(filename, "rb") as fp:
        line = fp.readline()
        while line:
            line=line.strip('\r\n')
            contract_set.append(line)
            line = fp.readline()

    return contract_set


def get_fund_data(iwb, symbol):
    url = 'http://hq.sinajs.cn/list=%s' % (symbol)
    c = iwb.get_web_contents(url)
    return c


def get_price(datas):
    datas = datas.split(',')
    price = float(datas[3])
    return price

        
def get_datetime(datas):
    datas = datas.split(',')
    date =  int(''.join(datas[30].split('-')))%1000000
    time = int(''.join(datas[31].split(':')))
    return date*1000000+time


def process_data(db, contract_set, rec_mgr):
    iwb = web.browser_tab()
    iwb.Connect('hq.sinajs.cn')

    print contract_set
    for contract in contract_set:
        contract_data = get_fund_data(iwb, contract)
        price = get_price(contract_data)
        datetime = get_datetime(contract_data)
        rec_mgr.set(db, contract, datetime, price)
    

if __name__ == '__main__':
    contract_set = load_contract("contract.ini")

    db_info = {
    # 'host'         : 'www.5656k.com',
        'host'         : '127.0.0.1',
        'user'         : 'root',
        'password'     : '1',
        'db'         : 'stock',
        'port'      : 3306
    }

    #创建日志目录
    if not os.path.exists("log"):
        os.mkdir("log")

    # 设置日志模式为追加
    log.set_log_mode('a')
    db = basefunc.create_database(db_info)
    rec_mgr = c_rec_manager()
    print "get_etf_data running!"

    while True:
        try:
            now_time = int(time.strftime('%m%d%H%M'))
            if not db.IsConnect(): db.ReConnect()

            if is_trade_local_time(now_time):
                process_data(db, contract_set, rec_mgr)
                time.sleep(1) # 休眠1秒
            else:
                time.sleep(5)
        except Exception, msg:
            try:
                if msg[0] == 2006:
                    db = basefunc.create_database(db_info)
                else:
                    print msg
            except Exception, msg:
                print msg
