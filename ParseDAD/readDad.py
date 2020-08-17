import  datetime
import  time
import struct
from exchange_config import *
from trade_day import *

def get_file_data(file_path):
    f = open(file_path,'rb')
    file_data = f.read()
    f.close()
    return file_data

class buf_reader(object):
    def __init__(this, data):
        this.data = data
        this.index = 0

    def seek(this, pos):
        this.index = pos

    def read_int(this):
        pack, = struct.unpack("<I", this.data[this.index:this.index+4])
        this.index += 4
        return pack

    def read_byte(this):
        pack, = struct.unpack("<B", this.data[this.index:this.index+1])
        this.index += 1
        return pack

    def read_short(this):
        pack, = struct.unpack("<H", this.data[this.index:this.index+2])
        this.index += 2
        return pack

    def read_double(this):
        pack, = struct.unpack("<f", this.data[this.index:this.index+4])
        this.index += 4
        return pack

#从外部文件读取所有tick数据
def parse_dad_ticks(file_path):
    HEAD_LEN = 66
    COUT_LEN = 4

    index = HEAD_LEN
    file_data = get_file_data(file_path)
    reader = buf_reader(file_data)
    reader.seek(index)
    index += COUT_LEN

    count = reader.read_int()
    print("read %d ticks" % count)

    all_ticks = []

    for x in xrange(0,count):
        reader.seek(index)
        index+= 50

        time_hm = reader.read_int()
        time_yd = reader.read_int()

        open        = reader.read_double()
        high        = reader.read_double()
        low         = reader.read_double()
        close       = reader.read_double()
        chicang     = reader.read_double()
        chengjiao   = reader.read_double()
        chengjiaoe  = reader.read_double()

        all_ticks.append([time_hm, time_yd, open, high, low, close, chengjiao])

    return all_ticks

#将tick时间戳转化为真实时间
def tick_to_time(tick, is_night):
    #起始时间戳，夜盘：2010年1月4日5时，白盘：2010年1月4日9时
    begin_magic = 1088659148
    datetime_begin = datetime.datetime(2010, 1, 4, 5, 0)
    if is_night:
        datetime_begin = datetime.datetime(2010, 1, 4, 5, 0)

    #tick经过的总分钟数
    pass_mins = (tick[1] - begin_magic) * 45 + tick[0] / (0xffffffff / 45)

    #tick所代表时间
    datetime_now = datetime_begin + datetime.timedelta(minutes = pass_mins)

    #若为周日21:00-24:00，或为周一0:00-2:30，将日期前移两位
    week_day = datetime_now.weekday()
    hour_min = int(datetime_now.strftime("%H%M"))
    if (6 == week_day and hour_min > 2100 and hour_min < 2400) \
        or (0 == week_day and hour_min >= 0 and hour_min <= 230):
        datetime_now = datetime_now - datetime.timedelta(days = 2)

    return datetime_now

#判断两个tick是否为同一日期集合
def is_not_same_day(tick, next_tick, is_night):
    delta = datetime.timedelta(hours=3, minutes=0)
    date_time = tick_to_time(tick, is_night) + delta
    next_date_time = tick_to_time(next_tick, is_night) + delta

    week_day = date_time.weekday()
    next_week_day = next_date_time.weekday()

    if date_time.date() != next_date_time.date() and not (week_day == 5 and next_week_day == 0):
        return True

    return False

#按日期区分tick
def parse_row_ticks(ticks, is_night):
    count = len(ticks)

    all_ticks = []
    day_ticks = []
    for x in xrange(0,count):
        tick = ticks[x]

        day_ticks.append(tick)

        # 当天是否结束
        is_end_day = False
        if x == count - 1 : is_end_day = True
        else:
            next_tick = ticks[x+1]
            if is_not_same_day(tick, next_tick, is_night): is_end_day = True

        if is_end_day:
            all_ticks.append(day_ticks)
            day_ticks = []

    return all_ticks

def main(input_file, output_file, gap_file, exg_ini, contract):
    #读取配置文件
    exg_cfg = exchange_config(exg_ini)
    #检测合约是否属于夜盘
    is_night = exg_cfg.is_night(contract)

    #中金所需要加4小时偏移
    exchage_name = exg_cfg.get_contract_exchage(contract)
    exchage_offset = 0
    if exchage_name == "CFFEX": exchage_offset = 4

    #读取所有tick
    row_ticks = parse_dad_ticks(input_file)
    #按日期区分tick
    all_ticks = parse_row_ticks(row_ticks, is_night)

    print("prcess %d day ticks" % len(all_ticks))

    def record_season(all_ticks):
        first_price = 0
        last_price = 0
        for day_ticks in all_ticks:
            #获取第一分钟数据
            first_tick = day_ticks[0]
            first_date_time = tick_to_time(first_tick, is_night)
            date = first_date_time.year * 10000 + first_date_time.month * 100 + first_date_time.day

            #检测是否有换手
            first_price = first_tick[2]
            if last_price != 0:
                diff_price = first_price - last_price
                if abs(diff_price) > last_price * 3 / 100:
                    gaps_str = "%d/%02d/%02d-%02d:%02d\t%.3f\t%.3f\t%.3f\n" % (first_date_time.year, first_date_time.month, first_date_time.day,
                                                                               first_date_time.hour, first_date_time.minute, last_price,
                                                                               first_price, diff_price)
                    yield gaps_str

            #获取最后一分钟数据
            last_idx = len(day_ticks) - 1
            last_tick = day_ticks[last_idx]

            last_price = last_tick[5]

    def make_line(all_ticks):
        for day_ticks in all_ticks:
            #获取当日所有有效分钟集合
            first_tick = day_ticks[0]
            first_date_time = tick_to_time(first_tick, is_night)
            date = first_date_time.year * 10000 + first_date_time.month * 100 + first_date_time.day
            day_mins = exg_cfg.get_contract_daymin(contract, date)

            #统计当日数据
            time_index = 0
            for min_tick in day_ticks:
                if 0 == min_tick[6]:
                    continue

                if time_index >= len(day_mins):
                    #收集的当日数据超出当日有效分钟数
                    print("%s index %d out of range %d" %(date, time_index, len(day_ticks)))
                else:
                    #将当前tick转换为时间字符串和期货价格字符串，并返回
                    min_date_time = tick_to_time(min_tick, is_night)
                    time_index += 1
                    time_str = "%d/%02d/%02d-%02d:%02d" % (min_date_time.year, min_date_time.month,
                                                           min_date_time.day, min_date_time.hour+exchage_offset,
                                                           min_date_time.minute)
                    tick_str = "%.2f\t%.2f\t%.2f\t%.2f\t%d" % (min_tick[2], min_tick[3],
                                                                 min_tick[4], min_tick[5],
                                                                 min_tick[6])

                    yield "%s\t%s\n" % (time_str, tick_str)

            #打印当日收集到的tick数
            if time_index != len(day_mins):
                print("%d 数据不全 %d/%d" %(date, time_index, len(day_mins)))

    # 记录换季跳空
    # fgaps = open(gap_file, "wt+")
    # for gaps_str in record_season(all_ticks):
    #   fgaps.write(gaps_str)
    # fgaps.close()

    # out put
    fout = open(output_file, "wt+")
    for line in make_line(all_ticks):
        fout.write(line)
    fout.close()

# if __name__ == '__main__':

#   contract = "jd"

#   input_file = "G:\stock_data\STOCKMIN1.DAD"
#   for line in make_line(all_ticks):
#       fout.write(line)
#   fout.close()

if __name__ == '__main__':

    contract = "ag"

    input_file = "c:\STOCKMIN1.DAD"
    # input_file = "C:/STOCKDAY.DAD"

    path_ini = "exchange.ini"
    output_file = "%sL0.txt" % contract
    gap_file = "%sgaps.txt" % contract
    main(input_file, output_file, gap_file, path_ini, contract)
