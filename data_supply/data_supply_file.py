# 需要补充的合约名字
SYMBOL = "p"

# 间隔多少小时直接跳过不补充
PASS_INTERVAL_HOURS = 16

#########################################
import re
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

def add_mins(minute, diff_mins):
    datetime_cur = datetime.datetime(2000 + minute/100000000, minute / 1000000 % 100, minute / 10000 % 100, minute / 100 % 100, minute % 100)
    datetime_next = datetime_cur + datetime.timedelta(minutes = diff_mins)
    minute_next = datetime_next.year % 100 * 100000000 + datetime_next.month * 1000000 + datetime_next.day * 10000 + datetime_next.hour * 100 + datetime_next.minute

    return minute_next

def diff_secs(first_min, second_min):
    datetime_first = datetime.datetime(2000 + first_min/100000000, first_min/1000000%100, first_min/10000%100, first_min/100%100,
                                       first_min % 100)
    datetime_second = datetime.datetime(2000 + second_min/100000000, second_min/1000000%100, second_min/10000 % 100, second_min/100%100,
                                        second_min % 100)
    delta = datetime_second - datetime_first

    return delta.days * 24 * 3600 + delta.seconds

def correct_time(miss_time, tar_time, set_time_area):
    date = miss_time / 10000
    min = miss_time % 10000

    diff_hours = diff_secs(miss_time, tar_time) / 3600
    # 时间间隔太多，直接跳过
    if diff_hours > PASS_INTERVAL_HOURS:
        min = set_time_area[0][0] + 1
        print "interval %d hours too long, from %d to %d" % (diff_hours, miss_time, tar_time)
        return tar_time / 10000 * 10000 + min

    # 缺失的时间在交易时间内，直接返回，不用修正
    for time_area in set_time_area:
        if (min >= time_area[0] and min <= time_area[1]):
            return miss_time

    # 缺失时间在全天交易时间段内，修正为下一段开始
    for time_area in set_time_area:
        if min > set_time_area[-1][1] and min < set_time_area[0][1] :
            break
        if min <= time_area[0]:
            min = time_area[0] + 1
            return date * 10000 + min

    # 缺失时间在全天交易时间外，取第一段开始，并修正为下个交易日
    min = set_time_area[0][0] + 1
    return tar_time / 10000 * 10000 + min


def parse_date(d):
    ma = re.match("(\d{4})/(\d{2})/(\d{2})-(\d{2}):(\d{2})", d)
    return (int(e) for e in ma.groups())

def read_file(file_name):
    list_data = []
    f = open(file_name, "rt")
    if f:
        l = f.readline()
        while l:
            gs = l[:-1].split('\t')
            y,m,d,h,mm = parse_date(gs[0])

            _open = float(gs[1])
            _hith = float(gs[2])
            _low  = float(gs[3])
            _close= float(gs[4])
            _num  = float(gs[5])
            _offset = float(gs[6])
            list_data.append([y,m,d,h,mm,_open,_hith,_low,_close,_num,_offset])
            l = f.readline()
        f.close()

    return list_data

def data_supply():
    list_data = read_file("%sL0.txt" % SYMBOL)
    if 0 == len(list_data):
        return

    exchange_info = exchange_config.exchange_config("Exchange.ini")

    f = open("new_%sL0.txt" % SYMBOL, "wt")
    if f:
        last_time = list_data[0][0] % 100 * 100000000 + list_data[0][1] * 1000000 + list_data[0][2] * 10000 + list_data[0][3] * 100 + list_data[0][4]
        last_data = []
        count = len(list_data)
        index = 1
        for data in list_data:
            time_cur = data[0] % 100 * 100000000 + data[1] * 1000000 + data[2] * 10000 + data[3] * 100 + data[4]

            if not exchange_info.is_in_exchange_time(SYMBOL, time_cur):
                print time_cur, "not in exchange time"
                continue

            set_time_area = exchange_info.get_contract_min_area(SYMBOL, 20000000 + last_time/10000)

            while index < count and last_time < time_cur:
                last_time = correct_time(last_time, time_cur, set_time_area)
                if last_time >= time_cur:
                    break

                if len(last_data) > 0:
                    f.write("%u/%02u/%02u-%02u:%02u\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (2000 + last_time/100000000,last_time/1000000%100,
                            last_time/10000%100,last_time/100%100,last_time%100,last_data[5],last_data[6],last_data[7],last_data[8],
                            last_data[9],last_data[10]))

                # print last_time,time_cur
                last_time = add_mins(last_time, 1)

            f.write("%u/%02u/%02u-%02u:%02u\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (data[0],data[1],data[2],data[3],data[4],data[5],data[6],
                    data[7],data[8],data[9],data[10]))

            last_time = add_mins(last_time, 1)
            last_data = data
            index += 1

        f.close()


if __name__ == '__main__':
    data_supply()

