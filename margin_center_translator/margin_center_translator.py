import ConfigParser
import log
import re
from datetime import date

def get_symbol(contract):
    ma = re.search("([A-Za-z]+)(\d+)", contract)
    if ma:
        arrs = ma.groups()
        symbol = arrs[0]
        return symbol
    return ""


def get_number(contract):
    ma = re.search("([A-Za-z]+)(\d+)", contract)
    if ma:
        arrs = ma.groups()
        symbol = arrs[1]
        return symbol
    return ""


def parse_head_ini():
    ini_info = {}

    conf = ConfigParser.ConfigParser()  
    #用config对象读取配置文件
    conf.read("head_type.ini")  

    sections = conf.sections()
    for section in sections:
        ini_info[section] = {}
        options = conf.options(section)
        for option in options:
            value = conf.get(section, option)
            value_info_set = value.split('|')
            for value_info in value_info_set:
                ini_info[section][value_info] = option

    return ini_info


def get_data_head(ini_info, head):
    head_ini_info = ini_info["header"]
    critical_ini_info = ini_info["critical"]

    head_index = {}
    head_info = head.split('\t')
    head_size = len(head_info)
    for i in xrange(0,head_size):
        if head_ini_info.has_key(head_info[i]):
            key = head_ini_info[head_info[i]]
            head_index[key] = i
        else:
            log.WriteLog("error", "文件[head_type.ini][header]中关键字[%s]未被配置" % head_info[i])

    for critical_info in critical_ini_info.keys():
        if not head_index.has_key(critical_info):
            log.WriteLog("error", "文件[head_type.ini][header]中critical关键字[%s]未被配置" % critical_info)

    return head_index


def read_symbol_ini():
    symbols = []
    with open("symbol.ini", "rb") as fp:
        symbol = fp.readline()
        while symbol:
            symbol = symbol.replace("\r\n", "")
            symbols.append(symbol)
            symbol = fp.readline()

    return symbols


def get_real_contract(fake_contract, trade_date, symbols):
    fake_symbol = get_symbol(fake_contract)
    period = int(get_number(fake_contract))

    if period < 1000:
        year = trade_date / 10000
        year_digits = year % 10
        year_tens_digits = year / 10 % 10

        period_hun_digits = period / 100 % 10;
        if period_hun_digits >= year_digits:
            period = period % 1000 + 1000 * year_tens_digits
        else:
            period = period % 1000 + 1000 * (year_tens_digits + 1)

    for symbol in symbols:
        if symbol.lower() == fake_symbol.lower():
            contract = "%s%u" % (symbol, period)
            return contract

    return fake_contract


def parse_bill(ini_info, symbols):
    head_index = {}
    bill_info_set = []
    cur_date = 0
    one_day_day_set = []
    one_day_night_set = []
    with open("bill.txt", "rb") as fp:
        line = fp.readline()
        while line:
            line = line.replace("\r\n", "")
            if len(head_index) == 0:
                head_index = get_data_head(ini_info, line)
            else:
                bill_info = line.split('\t')
                
                #处理合约名称
                fake_contract = bill_info[head_index["contract"]]
                real_contract = get_real_contract(fake_contract, int(bill_info[head_index["date"]].replace('-', '')), symbols)
                bill_info[head_index["contract"]] = real_contract

                #处理日期
                date_str = bill_info[head_index["date"]]
                date_str = date_str.replace("-", "")
                date = int(date_str)
                if cur_date == 0:
                    cur_date = date
                elif cur_date != date:
                    bill_info_set.extend(one_day_night_set)
                    bill_info_set.extend(one_day_day_set)
                    one_day_day_set = []
                    one_day_night_set = []
                    cur_date = date

                #处理时间
                hhmmss_str = bill_info[head_index["time"]]
                hhmmss_str = hhmmss_str.replace(":", "")
                hhmmss = int(hhmmss_str)

                if hhmmss > 200000:
                    tar_idx = 0
                    size = len(one_day_night_set)
                    for i in xrange(0,size):
                        hhmmss_night_str = one_day_night_set[size - 1 - i][head_index["time"]]
                        hhmmss_night_str = hhmmss_night_str.replace(":", "")
                        hhmmss_night = int(hhmmss_night_str)

                        if hhmmss >= hhmmss_night:
                            tar_idx = size - 1 - i + 1
                            break

                    if tar_idx >= size:
                        one_day_night_set.append(bill_info)
                    else:
                        one_day_night_set.insert(tar_idx, bill_info)
                else:
                    one_day_day_set.append(bill_info)

            line = fp.readline()

        bill_info_set.extend(one_day_night_set)
        bill_info_set.extend(one_day_day_set)

    return (head_index, bill_info_set)


def translate(head_index, bill_info_set):
    with open("trade_records.db", "wb") as fp:
        index = 1
        for bill_info in bill_info_set:
            date_str = bill_info[head_index["date"]].replace('-', '')
            time_str = bill_info[head_index["time"]]
            contract = bill_info[head_index["contract"]]
            dir_str = bill_info[head_index["dir"]].decode("gbk")
            if dir_str.find(u"买") >= 0:
                dir_str = u"买入"
            else:
                dir_str = u"卖出"
            type_str = bill_info[head_index["type"]].decode("gbk")
            if type_str.find(u"开") >= 0:
                type_str = u"开仓"
            else:
                type_str = u"平仓"
            price = float(bill_info[head_index["price"]].replace(',', ''))
            commission = float(bill_info[head_index["commission"]].replace(',', ''))
            amount = int(bill_info[head_index["amount"]])
            hedge = bill_info[head_index["hedge"]].decode("gbk")
            trade_no_str = bill_info[head_index["trade_no"]]
            trade_record = "%s\t%s\t%s\t%s\t%s\t%.4f\t%d\t%.4f\t%s\t%s\t%d\r\n" % (date_str, time_str, contract, dir_str.encode("gbk"), 
                type_str.encode("gbk"), price, amount, commission, hedge.encode("gbk"), trade_no_str, index)

            fp.write(trade_record)

            index = index + 1


def main():
    ini_info = parse_head_ini()
    symbols = read_symbol_ini()
    bill_info = parse_bill(ini_info, symbols)
    translate(bill_info[0], bill_info[1])


if __name__ == '__main__':
    main()