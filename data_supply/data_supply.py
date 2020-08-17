import db
import log
import time
import ConfigParser
import exchange_config
import datetime

def print_log(msg):
    # 设置日志模式为追加
    log.set_log_mode('a')

    now_datetime = time.localtime()
    content = u"%u-%u-%u %u:%u:%u %s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, now_datetime.tm_hour, 
              now_datetime.tm_min, now_datetime.tm_sec, msg)
    log.WriteLog("sys", content)

def get_symbol(contract):
    size = len(contract)
    tar_index = 0
    for i in xrange(0,size):
        if contract[i].isdigit():
            tar_index = i
            break

    return contract[:tar_index]

def add_min(minute, diff_mins):
    datetime_cur = datetime.datetime(2000 + minute/100000000, minute / 1000000 % 100, minute / 10000 % 100, minute / 100 % 100, minute % 100)
    datetime_next = datetime_cur + datetime.timedelta(minutes = diff_mins)
    minute_next = datetime_next.year % 100 * 100000000 + datetime_next.month * 1000000 + datetime_next.day * 10000 + datetime_next.hour * 100 + datetime_next.minute

    return minute_next

def correct_time(time, tar_time, set_time_area):
    date = time / 10000
    min = time % 10000

    find = False
    for time_area in set_time_area:
        if (min > time_area[0] and min <= time_area[1]) or min == 0:
            find = True
            break

    if not find:
        for time_area in set_time_area:
            if min <= time_area[0]:
                find = True
                min = time_area[0] + 1
                break

    if not find:
        min = set_time_area[0][0] + 1

    tar_min = tar_time % 10000
    if min <= tar_min:
        time = tar_time / 10000 * 10000 + min
    else:
        time = date * 10000 + min

    return time


class SystemConfig(object):
    # 配置文件信息结构
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.db_host = ini_parser.get("db", "host")
        self.db_user = ini_parser.get("db", "user")
        self.db_password = ini_parser.get("db", "password")
        self.db_db = ini_parser.get("db", "db")
        self.db_port = ini_parser.getint("db", "port")
        self.db_charset = ini_parser.get("db", "charset")

        self.table_name = ini_parser.get("table", "name")

        self.contract_ins = ini_parser.get("contract", "ins")

        self.time_begin = ini_parser.getint("time", "begin")
        self.time_end = ini_parser.getint("time", "end")

        self.sql_page_num = ini_parser.getint("sql", "page_num")


def data_supply():
    system_info = SystemConfig("system.ini")

    exchange_info = exchange_config.exchange_config("Exchange.ini")

    db_operator = db.DB(host=system_info.db_host, user=system_info.db_user, passwd=system_info.db_password, db=system_info.db_db, 
                        charset=system_info.db_charset, port=system_info.db_port)

    symbol = get_symbol(system_info.contract_ins)

    last_time = system_info.time_begin
    last_contract_info = []
    while last_time <= system_info.time_end:
        sql = "select * from %s where `InstrumentID`='%s' and `Time` >= %u and `Time` <= %u order by `Time` asc limit %u" % (
              system_info.table_name, system_info.contract_ins, last_time, system_info.time_end, system_info.sql_page_num)
        db_operator.Execute(sql)

        set_contract_info = db_operator.FetchAll()
        size = len(set_contract_info)
        if 0 == size:
            break

        set_time_area = exchange_info.get_contract_min_area(symbol, 20000000 + last_time/10000)
        
        for contract_info in set_contract_info:
            time_cur = contract_info[2]

            while last_time < time_cur:
                last_time = correct_time(last_time, time_cur, set_time_area)
                if last_time >= time_cur:
                    break

                if len(last_contract_info) > 0:
                    sql_insert = "insert into %s values(0,'%s',%u,%u,%u,%u,%u,%u)" % (system_info.table_name, system_info.contract_ins,
                                 last_time, last_contract_info[3], last_contract_info[4], last_contract_info[5], last_contract_info[6], 
                                 last_contract_info[7])
                    db_operator.Execute(sql_insert)

                    print_log(u"数据补充：合约[%s],时间戳[%u]" % (system_info.contract_ins, last_time))

                last_time = add_min(last_time, 1)

            last_time = add_min(last_time, 1)
            last_contract_info = contract_info

    while last_time <= system_info.time_end and len(last_contract_info) > 0:
        if exchange_info.is_in_exchange_time(symbol, last_time % 10000):
            sql_insert = "insert into %s values(0,'%s',%u,%u,%u,%u,%u,%u)" % (system_info.table_name, system_info.contract_ins,
                         last_time, last_contract_info[3], last_contract_info[4], last_contract_info[5], last_contract_info[6], 
                         last_contract_info[7])
            db_operator.Execute(sql_insert)

            print_log(u"数据补充：合约[%s],时间戳[%u]" % (system_info.contract_ins, last_time))

        last_time = add_min(last_time, 1)


if __name__ == '__main__':
	data_supply()