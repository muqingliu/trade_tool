import re
import os
import sys
import log
import time
import ConfigParser
import exchange_config
import datetime

def print_log(msg):
    log.set_log_mode('a')

    now_datetime = time.localtime()
    content = u"%u-%u-%u %u:%u:%u %s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, now_datetime.tm_hour, 
              now_datetime.tm_min, now_datetime.tm_sec, msg)
    log.WriteLog("sys", content)

def read_file(file_name):
    list_data = []
    f = open(file_name, "rt")
    if f:
        l = f.readline()
        while l:
            try:
                ma = re.findall("(\d+)/(\d+)/(\d+)-(\d+):(\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)$", l)
                if ma:
                    y = int(ma[0][0])
                    m = int(ma[0][1])
                    d = int(ma[0][2])
                    h = int(ma[0][3])
                    mm= int(ma[0][4])
                    _open = float(ma[0][5])
                    _hith = float(ma[0][6])
                    _low  = float(ma[0][7])
                    _close= float(ma[0][8])
                    _num  = float(ma[0][9])
                    list_data.append([y,m,d,h,mm,_open,_hith,_low,_close,_num])
            except Exception, e:
                print e
            l = f.readline()
        f.close()

    return list_data

def CalcAverage(set_num):
    total = sum(set_num)
    length = len(set_num)
    if 0 == length:
        return 0

    return total / length

class SystemConfig(object):
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        bar_index = path_ini.find("_")
        if -1 == bar_index:
            return

        symbol = path_ini[:bar_index]

        self.map_last_trade_day = {}
        set_section = ["01","05","09"]
        for section in set_section:
            self.map_last_trade_day[section] = []

            for i in xrange(1,100):
                key = "day%u" % i
                try:
                    date = ini_parser.getint(section, key)
                except Exception, e:
                    break

                self.map_last_trade_day[section].append(date)

        self.min_volume = ini_parser.getint("main", "min_volume")
        self.average_num = ini_parser.getint("main", "average_num")
        self.merge = ini_parser.getint("main", "merge")
        self.filter_by_wrap = ini_parser.getint("main", "filter_by_wrap")

def get_compare_data(list_date_1, list_date_2, set_last_trade_volume_1, set_last_trade_volume_2, last_data_1, last_data_2, index_1, index_2, min_volume, average_num):
    data_1 = list_date_1[index_1]
    data_2 = list_date_2[index_2]

    day_1 = data_1[0] % 100 * 100000000 + data_1[1] * 1000000 + data_1[2] * 10000 + data_1[3] * 100 + data_1[4]
    day_2 = data_2[0] % 100 * 100000000 + data_2[1] * 1000000 + data_2[2] * 10000 + data_2[3] * 100 + data_2[4]

    compare_data_1 = []
    compare_data_2 = []
    if day_1 == day_2:
        compare_data_1 = data_1
        compare_data_2 = data_2
        last_data_1 = data_1
        last_data_2 = data_2
        index_1 = index_1 + 1
        index_2 = index_2 + 1
    elif day_1 > day_2:
        compare_data_1 = last_data_1
        day_1 = day_2
        compare_data_2 = data_2
        last_data_2 = data_2
        index_2 = index_2 + 1
    else:
        compare_data_2 = last_data_2
        day_2 = day_1
        compare_data_1 = data_1
        last_data_1 = data_1
        index_1 = index_1 + 1

    if len(compare_data_1) == 0 or len(compare_data_2) == 0:
        return [], [], day_1, day_2, last_data_1, last_data_2, index_1, index_2

    set_last_trade_volume_1.append(compare_data_1[9])
    set_last_trade_volume_2.append(compare_data_2[9])
    length_1 = len(set_last_trade_volume_1)
    length_2 = len(set_last_trade_volume_2)
    if length_1 < average_num or length_2 < average_num:
        return [], [], day_1, day_2, last_data_1, last_data_2, index_1, index_2

    if length_1 > average_num:
        del set_last_trade_volume_1[0]

    if length_2 > average_num:
        del set_last_trade_volume_2[0]

    if CalcAverage(set_last_trade_volume_1) < min_volume or CalcAverage(set_last_trade_volume_2) < min_volume:
        return [0], [0], day_1, day_2, last_data_1, last_data_2, index_1, index_2

    return compare_data_1, compare_data_2, day_1, day_2, last_data_1, last_data_2, index_1, index_2

def diff_output_single(data_path, symbol, period_1, period_2, min_volume, average_num, filter_by_wrap, map_last_trade_day):
    file_name_1 = "%s\\%s%s.txt" % (data_path, symbol, period_1)
    file_name_2 = "%s\\%s%s.txt" % (data_path, symbol, period_2)
    list_date_1 = read_file(file_name_1)
    list_date_2 = read_file(file_name_2)

    list_last_trade_day = []
    list_last_trade_day.extend(map_last_trade_day[period_1])
    list_last_trade_day.extend(map_last_trade_day[period_2])
    list_last_trade_day.sort()

    last_trade_day_index = 0
    last_trade_day = list_last_trade_day[0]

    set_last_trade_volume_1 = []
    set_last_trade_volume_2 = []

    output_file = "%s\\%s_%s_%s_%u_diff_output.txt" % (data_path, symbol, period_1, period_2, last_trade_day)
    f = open(output_file, "wt")
    if f:
        last_data_1 = []
        last_data_2 = []
        index_1 = 0
        index_2 = 0
        while index_1 < len(list_date_1) and index_2 < len(list_date_2):
            compare_data_1, compare_data_2, day_1, day_2, last_data_1, last_data_2, index_1, index_2 = get_compare_data(list_date_1, \
                list_date_2, set_last_trade_volume_1, set_last_trade_volume_2, last_data_1, last_data_2, index_1, index_2, min_volume, average_num)
            if len(compare_data_1) <= 1 or len(compare_data_2) <= 1:
                if filter_by_wrap and len(compare_data_1) == 1 and len(compare_data_2) == 1:
                    f.write("\n")
                continue

            if 20000000 + day_1 / 10000 > last_trade_day:
                f.close()

                if last_trade_day_index + 1 < len(list_last_trade_day):
                    last_trade_day_index = last_trade_day_index + 1
                    last_trade_day = list_last_trade_day[last_trade_day_index]

                    output_file = "%s\\%s_%s_%s_%u_diff_output.txt" % (data_path, symbol, period_1, period_2, last_trade_day)
                    f = open(output_file, "wt")
                    if not f:
                        break
                else:
                    last_trade_day = 99999999

                    output_file = "%s_%s_%s_%u_diff_output.txt" % (symbol, period_1, period_2, last_trade_day)
                    f = open(output_file, "wt")
                    if not f:
                        break

            f.write("%u/%02u/%02u-%02u:%02u\t%.2f\n" % (2000+day_1/100000000, day_1/1000000%100, day_1/10000%100, day_1/100%100, day_1%100, \
                    compare_data_1[8] - compare_data_2[8]))

        f.close()

def diff_output_merge(data_path, symbol, period_1, period_2, min_volume, average_num, filter_by_wrap, map_last_trade_day):
    file_name_1 = "%s\\%s%s.txt" % (data_path, symbol, period_1)
    file_name_2 = "%s\\%s%s.txt" % (data_path, symbol, period_2)
    list_date_1 = read_file(file_name_1)
    list_date_2 = read_file(file_name_2)
    period_1_num = int(period_1)
    period_2_num = int(period_2)

    list_last_trade_day = []

    for date in map_last_trade_day[period_1]:
        date_period = date * 100 + period_1_num
        list_last_trade_day.append(date_period)

    for date in map_last_trade_day[period_2]:
        date_period = date * 100 + period_2_num
        list_last_trade_day.append(date_period)

    list_last_trade_day.sort()

    last_trade_day_index = 0
    last_trade_day = list_last_trade_day[0] / 100
    last_period = list_last_trade_day[0] % 100

    set_last_trade_volume_1 = []
    set_last_trade_volume_2 = []

    output_file_period_1 = "%s\\%s_%s_%s_same.log" % (data_path, symbol, period_1, period_2)
    output_file_period_2 = "%s\\%s_%s_%s_diff.log" % (data_path, symbol, period_1, period_2)
    slice_key_1 = "%s_%s_%s_same.log" % (symbol, period_1, period_2)
    slice_key_2 = "%s_%s_%s_diff.log" % (symbol, period_1, period_2)
    if period_1_num > period_2_num:
        output_file_period_1 = "%s\\%s_%s_%s_diff.log" % (data_path, symbol, period_1, period_2)
        output_file_period_2 = "%s\\%s_%s_%s_same.log" % (data_path, symbol, period_1, period_2)
        slice_key_1 = "%s_%s_%s_diff.log" % (symbol, period_1, period_2)
        slice_key_2 = "%s_%s_%s_same.log" % (symbol, period_1, period_2)

    map_time_slice = {}
    map_time_slice[slice_key_1] = []
    map_time_slice[slice_key_2] = []

    f_1 = open(output_file_period_1, "wt")
    f_2 = open(output_file_period_2, "wt")
    if f_1 and f_2:
        last_data_1 = []
        last_data_2 = []
        index_1 = 0
        index_2 = 0
        first_day = 0
        last_day = 0
        while index_1 < len(list_date_1) and index_2 < len(list_date_2):
            compare_data_1, compare_data_2, day_1, day_2, last_data_1, last_data_2, index_1, index_2 = get_compare_data(list_date_1, \
                list_date_2, set_last_trade_volume_1, set_last_trade_volume_2, last_data_1, last_data_2, index_1, index_2, min_volume, average_num)
            if len(compare_data_1) <= 1 or len(compare_data_2) <= 1:
                if filter_by_wrap and len(compare_data_1) == 1 and len(compare_data_2) == 1:
                    if last_period == period_1_num: 
                        f_1.write("\n")
                    elif last_period == period_2_num:
                        f_2.write("\n")
                continue

            if first_day == 0:
                first_day = day_1

            if 20000000 + day_1 / 10000 > last_trade_day:
                if last_trade_day_index + 1 < len(list_last_trade_day):
                    if last_period == period_1_num:
                        map_time_slice[slice_key_1].append([first_day, last_day])
                    elif last_period == period_2_num:
                        map_time_slice[slice_key_2].append([first_day, last_day])

                    last_trade_day_index = last_trade_day_index + 1
                    last_trade_day = list_last_trade_day[last_trade_day_index] / 100
                    last_period = list_last_trade_day[last_trade_day_index] % 100

                    first_day = day_1

            last_day = day_1

            if last_period == period_1_num:
                f_1.write("%u/%02u/%02u-%02u:%02u\t%.2f\n" % (2000+day_1/100000000, day_1/1000000%100, day_1/10000%100, day_1/100%100, \
                        day_1%100, compare_data_1[8] - compare_data_2[8]))
            elif last_period == period_2_num:
                f_2.write("%u/%02u/%02u-%02u:%02u\t%.2f\n" % (2000+day_1/100000000, day_1/1000000%100, day_1/10000%100, day_1/100%100, \
                        day_1%100, compare_data_1[8] - compare_data_2[8]))

        if last_period == period_1_num:
            map_time_slice[slice_key_1].append([first_day, last_day])
        elif last_period == period_2_num:
            map_time_slice[slice_key_2].append([first_day, last_day])

        write_time_slice(data_path, map_time_slice)

        f_1.close()
        f_2.close()

def write_time_slice(data_path, map_time_slice):
    output_time_slice = "%s\\time_slice.cfg" % (data_path)
    f_slice = open(output_time_slice, "at")
    if f_slice:
        for key in map_time_slice.keys():
            set_time_slice = map_time_slice.get(key)
            size = len(set_time_slice)
            for i in xrange(0, size):
                time_slice = set_time_slice[i]
                str_time_slice = "%s\t%u/%02u/%02u-%02u:%02u\t%u/%02u/%02u-%02u:%02u\n" % (key, 2000+time_slice[0]/100000000, \
                    time_slice[0]/1000000%100, time_slice[0]/10000%100, time_slice[0]/100%100, time_slice[0]%100, \
                    2000+time_slice[1]/100000000, time_slice[1]/1000000%100, time_slice[1]/10000%100, time_slice[1]/100%100, \
                    time_slice[1]%100)
                f_slice.write(str_time_slice)

        f_slice.close()


def main(data_path):
    try:
        file_list = []
        for root,dirs,files in os.walk(data_path):
            for filespath in files:
                file_list.append(os.path.join(root,filespath))

        file_cfg = ""
        cfg_index = -1

        length = len(file_list)
        for i in xrange(0, length):
            if file_list[i].find("cfg") >= 0:
                file_cfg = file_list[i]
                cfg_index = i

        if cfg_index < 0 or len(file_cfg) == 0:
            return

        system_info = SystemConfig(file_cfg)
        del file_list[cfg_index]
        length = len(file_list)

        bar_index = file_cfg.rfind("_")
        slash_index = file_cfg.rfind("\\")
        if bar_index < 0 or slash_index < 0:
            return

        symbol = file_cfg[slash_index+1:bar_index]

        for i in xrange(0,length):
            index_1 = i
            index_2 = i + 1
            if index_2 >= length:
                index_2 = 0

            point_index_1 = file_list[index_1].rfind('.')
            if point_index_1 == -1:
                continue

            period_1 = file_list[index_1][point_index_1-2:point_index_1]

            point_index_2 = file_list[index_2].rfind('.')
            if point_index_2 == -1:
                continue

            period_2 = file_list[index_2][point_index_2-2:point_index_2]

            if not system_info.merge:
                diff_output_single(data_path, symbol, period_1, period_2, system_info.min_volume, system_info.average_num, system_info.filter_by_wrap, system_info.map_last_trade_day)
            else:
                diff_output_merge(data_path, symbol, period_1, period_2, system_info.min_volume, system_info.average_num, system_info.filter_by_wrap, system_info.map_last_trade_day)
    except Exception, e:
        print e
        os.system("pause")


#main(sys.argv[1])
main("E:\\trader_work\\tools\\data_supply\\data")

os.system("pause")