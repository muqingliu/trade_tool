from common import db
from common import define
import re


# 交易日期类型
TRADE_DATE_TYPE = define.enum(month = 0, quarter = 1, halfyear =2 )

db_info = {
	'host' 		: '192.168.1.101',
	'user' 		: 'root',
	'password' 	: 'w1c4h7',
	'db' 		: 'stock_data',
    'port'      : 3306
}

def create_database(info=None):
    if info == None: info = db_info

    return db.DB(host=info['host'],user=info['user'], passwd=info['password'], db=info['db'], port=info['port'])

def make_date(date_str):
	if date_str == '--': return 0
	date_arr = date_str.split('-')

	if len(date_arr) == 3:
		return int(date_arr[0])*10000+int(date_arr[1])*100+int(date_arr[2])
	return None

def get_number(str):
	if str == '--':	return 0
	m = re.match('(-{0,1}\d+\.{0,1}\d*).*', str)
	if m: return float(m.groups()[0])
	else: return 0

def get_bignumber(str):
	if str == '--':	return 0
	m = re.match('(-{0,1}\d+[,\d+]*\.{0,1}\d*).*', str)
	if m: return float(m.groups()[0].replace(',',''))
	else: return 0

def parse_tds(trs):
	tds = trs.findAll("td")
	return [tdc.text for tdc in tds]

# 找不同
def find_diff(base, iters):
    return [s for s in iters if s not in base]

# 向前获取最近的日期
def get_pre_date_nearby(datetime, date_type = TRADE_DATE_TYPE.quarter):
    date_range = [131,231,331,431,531,630,731,831,931,1031,1131,1231]
    if TRADE_DATE_TYPE.quarter == date_type:
        date_range = [331,630,931,1231]
    elif TRADE_DATE_TYPE.halfyear == date_type:
        date_range = [630,1231]

    mmdd = datetime % 10000
    yyyy = datetime/10000
    calc_datetime = 0
    for d in date_range[::-1]:
        if mmdd > d:
            calc_datetime = d
            break

    if calc_datetime == 0:
        calc_datetime = date_range[-1:][0]
        yyyy -= 1
    return yyyy*10000+calc_datetime

# 向后获取最近的日期
def get_next_date_nearby(datetime, date_type = TRADE_DATE_TYPE.quarter):
    date_range = [131,231,331,431,531,631,731,831,931,1031,1131,1231]
    if TRADE_DATE_TYPE.quarter == date_type:
        date_range = [331,631,931,1231]
    elif TRADE_DATE_TYPE.halfyear == date_type:
        date_range = [631,1231]

    mmdd = datetime % 10000
    yyyy = datetime/10000
    calc_datetime = 0
    for d in date_range:
        if mmdd < d:
            calc_datetime = d
            break

    if calc_datetime == 0:
        calc_datetime = date_range[0]
        yyyy += 1
    return yyyy*10000+calc_datetime

if __name__ == '__main__':
    print get_pre_time_nearby(20110131, TRADE_DATE_TYPE.month)