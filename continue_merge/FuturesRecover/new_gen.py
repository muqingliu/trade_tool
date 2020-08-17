# -*- coding: utf-8 -*-
# @Time    : 2017/12/4 15:11
# @Author  : hc
# @Site    :
# @File    : new_gen.py
# @Software: PyCharm

# F:\trade_tools_py\define\db_define.py 配置数据库连接信息
# 通过gaps获取换期时间。
from common import basefunc
from common import log
import re

# 合约-交易所
Instrument_info = {
    "rb": "hq_shfe_k1",  # 螺纹钢-上海期货交易所
    "ru": "hq_shfe_k1",
    "hc": "hq_shfe_k1",
    "ni": "hq_shfe_k1",
    "i": "hq_dce_k1",
    "j": "hq_dce_k1",
    "jm": "hq_dce_k1",
}
# 合约换期对应期数
Instrument_details = {}
Instrument_details["rb"] = [
    "1410",
    "1501",
    "1505",
    "1510",
    "1601",
    "1605",
    "1610",
    "1701",
    "1705",
    "1710",
    "1801",
    "1805",
]
Instrument_details["ru"] = [
    "1409",
    "1501",
    "1505",
    "1509",
    "1601",
    "1605",
    "1609",
    "1701",
    "1705",
    "1709",
    "1801",
    "1805",
]
Instrument_details["hc"] = [
    "1410",
    "1501",
    "1505",
    "1510",
    "1601",
    "1605",
    "1610",
    "1701",
    "1705",
    "1710",
    "1801",
    "1805",
]
Instrument_details["ni"] = [
    "1509",
    "1601",
    "1605",
    "1609",
    "1701",
    "1705",
    "1709",
    "1801",
    "1805",
]
Instrument_details["i"] = [
    "1409",
    "1501",
    "1505",
    "1509",
    "1601",
    "1605",
    "1609",
    "1701",
    "1705",
    "1709",
    "1801",
    "1805",
]
Instrument_details["j"] = [
    "1409",
    "1501",
    "1505",
    "1509",
    "1601",
    "1605",
    "1609",
    "1701",
    "1705",
    "1709",
    "1801",
    "1805",
]
Instrument_details["jm"] = [
    "1409",
    "1501",
    "1505",
    "1509",
    "1601",
    "1605",
    "1609",
    "1701",
    "1705",
    "1709",
    "1801",
    "1805",
]


class NEW_GEN:
    def __init__(self):
        self.db = basefunc.create_database()
        self.gaps = []

    # 查看数量是否匹配
    def chk_Instrument_details(self, instrument_name):
        if len(self.gaps) + 1 == len(Instrument_details[instrument_name]):
            return True
        print("gaps 和 Instrument_details 数量配置不一致。")
        return False

    # 构造查询sql 的时间参数
    def gen_date_list(self, instrument_name):
        if self.chk_Instrument_details(instrument_name):
            date_list = []
            l = len(self.gaps)
            for idx in range(-1,l):
                begin = ['2000/01/01', '09:01'] if idx == -1 else self.gaps[idx]
                end = ['2099/12/31', '21:01'] if idx == l - 1 else self.gaps[idx + 1]
                date_list.append([begin, end, Instrument_details[instrument_name][idx+1]])
            return date_list

    def get_data(self, instrument_name):
        l = self.gen_date_list(instrument_name)
        if not l:
            return

        sql = """select `id`,`InstrumentID`,`Time`,`OpenPrice`,`ClosePrice`,`HighestPrice`,`LowestPrice`,`Volume`
            from %s
            where InstrumentID  = \"%s\"
            AND Time BETWEEN %s AND %s
            ORDER BY Time ASC"""

        data = []
        data_source = []
        sum_dif = 0

        for d in l:
            dif = 0
            begin = d[0][0].replace("/", "")[2:] + d[0][1].replace(":", "")
            end = d[1][0].replace("/", "")[2:] + d[1][1].replace(":", "")
            instrument_ID = instrument_name + d[2]
            print(
                "begin[%s]end[%s]instrument_ID[%s]" %
                (begin, end, instrument_ID))
            q = sql % (Instrument_info[instrument_name],
                       instrument_ID, begin, end)
            self.db.Query(q)

            if data:  # 如果有数据。则开始计算点差
                r = self.db.FetchOne()
                while r[7] == 0:
                    r = self.db.FetchOne()
                    
                print(data[-1])
                c_d = data[-1][5]
                c_r = r[4]
                dif = c_r - c_d
                sum_dif += dif
                print("当期点差为%s-%s=[%s],累计点差[%s]" % (c_r, c_d, dif, sum_dif))
                data.pop()
                data.append([r[1],
                             r[2],
                             r[3] - dif,
                             r[5] - dif,
                             r[6] - dif,
                             r[4] - dif,
                             r[7]])

                data_source.pop()
                data_source.append([r[1],
                                    r[2],
                                    r[3],
                                    r[5],
                                    r[6],
                                    r[4],
                                    r[7]])

            r = self.db.FetchAll()
            for _r in r:
                if _r[7] == 0:
                    continue

                data.append([_r[1],
                             _r[2],
                             _r[3] - dif,
                             _r[5] - dif,
                             _r[6] - dif,
                             _r[4] - dif,
                             _r[7]])
                data_source.append([_r[1],
                                    _r[2],
                                    _r[3],
                                    _r[5],
                                    _r[6],
                                    _r[4],
                                    _r[7]])
        return data, data_source

    def format_log(self, filename, d, instrument_name):
        for _d in d:
            instrumentID = _d[0]
            s_time = str(_d[1])
            time = "20" + s_time[0:2] + "/" + s_time[2:4] + "/" + \
                s_time[4:6] + "-" + s_time[6:8] + ":" + s_time[8:10]
            OpenPrice = _d[2]
            HighestPrice = _d[3]
            LowestPrice = _d[4]
            ClosePrice = _d[5]
            Volume = _d[6]
            # log.WriteLog(filename,instrument_name+"\t%s\t%s\t%0.2f\t%s\t%s\t%s\t%s"%
            #              (instrumentID,time,OpenPrice,HighestPrice,LowestPrice,ClosePrice,Volume))
            log.WriteLog(
                filename, "%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f" %
                (time, OpenPrice, HighestPrice, LowestPrice, ClosePrice, Volume))

    def gen_data(self, instrument_name):
        self.gaps = []
        self.gaps = get_gaps(instrument_name)
        d, s = self.get_data(instrument_name)
        # self.format_log("data",d,instrument_name)
        self.format_log(instrument_name + "L0", s, instrument_name)


# 读取 rbgaps 配置文件。并格式化日期和
# 时间
def get_gaps(symbol):
    f = open("config/%sgaps.txt" % symbol)
    r = []
    for l in f:
        d = re.findall(r'\d{4}/\d{2}/\d{2}|\d{2}:\d{2}', l)
        r.append(d)
    return r


if __name__ == '__main__':
    o = NEW_GEN()
    for symbol in Instrument_info.keys():
        print symbol
        o.gen_data(symbol)
