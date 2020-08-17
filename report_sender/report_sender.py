import os
import ConfigParser
import httppost
import time
import re
from datetime import datetime
from xml.dom.minidom import Document

class SystemConfig(object):
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.goods_report_url=ini_parser.get("main", "goods_report_url")
        self.trade_rec_report_url=ini_parser.get("main", "trade_rec_report_url")
        self.trade_rec_max_num=ini_parser.get("main", "trade_rec_max_num")
        self.err_order_rec_report_url=ini_parser.get("main", "err_order_rec_report_url")
        self.err_order_rec_max_num = ini_parser.get("main", "err_order_rec_max_num")
        self.real_goods_report_url=ini_parser.get("main", "real_goods_report_url")
        self.report_dir=ini_parser.get("main", "report_dir")


def post_report(url, data):
    return httppost.httpPost(url, data)


def compare_tr_data(data1, data2):
    sys1 = int(data1[8])
    sys2 = int(data2[8])

    if data1[1] > data2[1]:
        return 1
    elif data1[1] == data2[1] and sys1 > sys2:
        return 1

    return -1


def read_tr_db(filename):
    list_data = []

    index = 1
    f = open(filename, "rb")
    if f:
        line = f.readline()
        while line:
            arrs = line.decode('gbk').split('\t')

            date = int(arrs[0])
            time_str = arrs[1]
            arrs_time = time_str.split(':')
            hh = int(arrs_time[0])
            mm = int(arrs_time[1])
            ss = int(arrs_time[2])
            contract = arrs[2]
            trade_dir = arrs[3]
            trade_type = arrs[4]
            price = float(arrs[5])
            trade_num = int(arrs[6])
            commission = float(arrs[7])
            sysID = ""
            if len(arrs) >= 9:
                if arrs[8] == u"投机" or arrs[8] == u"交割":
                    sysID = int(arrs[10])
                else:
                    sysID = int(arrs[8])

            # ma1 = re.search("(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+(\S+)", line)
            # ma2 = re.search("(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
            # if ma1:
            #     arrs = ma1.groups()
            #     date = int(arrs[0])
            #     hh = int(arrs[1])
            #     mm = int(arrs[2])
            #     ss = int(arrs[3])
            #     contract = arrs[4]
            #     trade_dir = arrs[5].decode('gbk')
            #     trade_type = arrs[6].decode('gbk')
            #     price = float(arrs[7])
            #     trade_num = int(arrs[8])
            #     commission = float(arrs[9])
            #     touji = arrs[10]
            #     sysID = int(arrs[11])

            #     list_data.append([contract, date%1000000, hh*10000+mm*100+ss, trade_dir, trade_type, price, trade_num, commission, sysID])
            # elif ma2:
            #     arrs = ma2.groups()
            #     date = int(arrs[0])
            #     hh = int(arrs[1])
            #     mm = int(arrs[2])
            #     ss = int(arrs[3])
            #     contract = arrs[4]
            #     trade_dir = arrs[5].decode('gbk')
            #     trade_type = arrs[6].decode('gbk')
            #     price = float(arrs[7])
            #     trade_num = int(arrs[8])
            #     commission = float(arrs[9])
            #     sysID = int(arrs[10])

            list_data.append([contract, date%1000000, hh*10000+mm*100+ss, trade_dir, trade_type, price, trade_num, commission, sysID])
            # else:
            #     print "line %d not match!" % (index)

            index = index + 1

            line = f.readline()
        f.close()

    return list_data


def produce_tr_set_xml(brokerID, userID, report_name, list_data, max_send_num, lastest_date_str, lastest_sys_id_str):
    doc = Document()

    root_ele = doc.createElement('root')
    doc.appendChild(root_ele)

    trader_ele = doc.createElement('trader1')
    root_ele.appendChild(trader_ele)

    time_ele = doc.createElement('time')
    cur_time = time.time()
    time_text = doc.createTextNode("%u" % cur_time)
    time_ele.appendChild(time_text)
    trader_ele.appendChild(time_ele)

    name_ele = doc.createElement("name")
    name_text = doc.createTextNode(report_name)
    name_ele.appendChild(name_text)
    trader_ele.appendChild(name_ele)

    broker_id_ele = doc.createElement("brokerID")
    broker_id_text = doc.createTextNode(brokerID)
    broker_id_ele.appendChild(broker_id_text)
    trader_ele.appendChild(broker_id_ele)

    user_id_ele = doc.createElement("userID")
    user_id_text = doc.createTextNode(userID)
    user_id_ele.appendChild(user_id_text)
    trader_ele.appendChild(user_id_ele)

    lastest_date = int(lastest_date_str)
    lastest_sys_id = int(lastest_sys_id_str)

    index = 0
    size = len(list_data)
    for i in xrange(0,size):
        data = list_data[i]
        date = data[1]
        sys_id = int(data[8])

        if date < lastest_date or (date == lastest_date and sys_id <= lastest_sys_id):
            continue

        if index < int(max_send_num):
            trade_rec_ele = doc.createElement("trade_rec%u" % (index + 1))
            trader_ele.appendChild(trade_rec_ele)

            produce_tr_xml(doc, trade_rec_ele, data)

            index = index + 1
        else:
            break

    result = doc.toprettyxml(indent = '')

    return (result, index)


def produce_tr_xml(doc, trade_rec_ele, data):
    contract_ele = doc.createElement("contract")
    contract_text = doc.createTextNode(data[0])
    contract_ele.appendChild(contract_text)
    trade_rec_ele.appendChild(contract_ele)

    sys_ele = doc.createElement("sys_id")
    sys_text = doc.createTextNode("%u" % data[8])
    sys_ele.appendChild(sys_text)
    trade_rec_ele.appendChild(sys_ele)

    trade_date_ele = doc.createElement("trade_date")
    trade_date_text = doc.createTextNode("%u" % data[1])
    trade_date_ele.appendChild(trade_date_text)
    trade_rec_ele.appendChild(trade_date_ele)

    trade_time_ele = doc.createElement("trade_time")
    trade_time_text = doc.createTextNode("%u" % data[2])
    trade_time_ele.appendChild(trade_time_text)
    trade_rec_ele.appendChild(trade_time_ele)

    buy_type_ele = doc.createElement("buy_type")
    buy_type_text = doc.createTextNode(data[4])
    buy_type_ele.appendChild(buy_type_text)
    trade_rec_ele.appendChild(buy_type_ele)

    buy_dir_ele = doc.createElement("buy_dir")
    buy_dir_text = doc.createTextNode(data[3])
    buy_dir_ele.appendChild(buy_dir_text)
    trade_rec_ele.appendChild(buy_dir_ele)

    price_ele = doc.createElement("price")
    price_text = doc.createTextNode("%f" % data[5])
    price_ele.appendChild(price_text)
    trade_rec_ele.appendChild(price_ele)

    profit_ele = doc.createElement("profit")
    profit_text = doc.createTextNode("0.00")
    profit_ele.appendChild(profit_text)
    trade_rec_ele.appendChild(profit_ele)

    total_profit_ele = doc.createElement("total_profit")
    total_profit_text = doc.createTextNode("0.00")
    total_profit_ele.appendChild(total_profit_text)
    trade_rec_ele.appendChild(total_profit_ele)

    commission_ele = doc.createElement("commission")
    commission_text = doc.createTextNode("%f" % data[7])
    commission_ele.appendChild(commission_text)
    trade_rec_ele.appendChild(commission_ele)

    number_ele = doc.createElement("number")
    number_text = doc.createTextNode("%u" % data[6])
    number_ele.appendChild(number_text)
    trade_rec_ele.appendChild(number_ele)


def compare_eor_data(data1, data2):
    ref1 = int(data1[8])
    ref2 = int(data2[8])

    if data1[3] > data2[3]:
        return 1
    elif data1[3] == data2[3] and ref1 > ref2:
        return 1

    return -1


def read_eor_db(filename):
    list_data = []

    index = 1
    f = open(filename, "rb")
    if f:
        line = f.readline()
        while line:
            arrs = line.split('\t')

            contract = arrs[0]
            trade_type = arrs[1].decode('gbk')
            trade_dir = arrs[2].decode('gbk')
            date = int(arrs[3])
            time = int(arrs[4])
            trade_num = int(arrs[5])
            price = float(arrs[6])
            err_msg = arrs[7].decode('gbk')
            ref_id = int(arrs[8])

            # ma = re.search("(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
            # if ma:
            #     arrs = ma.groups()
            #     contract = arrs[0]
            #     trade_type = arrs[1].decode('gbk')
            #     trade_dir = arrs[2].decode('gbk')
            #     date = int(arrs[3])
            #     time = int(arrs[4])
            #     trade_num = int(arrs[5])
            #     price = float(arrs[6])
            #     err_msg = arrs[7].decode('gbk')
            #     ref_id = int(arrs[8])

            list_data.append([contract, trade_type, trade_dir, date % 1000000, time, trade_num, price, err_msg, ref_id])
            # else:
            #     print "line %d not match!" % (index)

            index = index + 1

            line = f.readline()
        f.close()

    return list_data


def produce_eor_set_xml(brokerID, userID, report_name, list_data, max_send_num, lastest_date_str, lastest_sys_id_str):
    doc = Document()

    root_ele = doc.createElement('root')
    doc.appendChild(root_ele)

    trader_ele = doc.createElement('trader1')
    root_ele.appendChild(trader_ele)

    time_ele = doc.createElement('time')
    cur_time = time.time()
    time_text = doc.createTextNode("%u" % cur_time)
    time_ele.appendChild(time_text)
    trader_ele.appendChild(time_ele)

    name_ele = doc.createElement("name")
    name_text = doc.createTextNode(report_name)
    name_ele.appendChild(name_text)
    trader_ele.appendChild(name_ele)

    broker_id_ele = doc.createElement("brokerID")
    broker_id_text = doc.createTextNode(brokerID)
    broker_id_ele.appendChild(broker_id_text)
    trader_ele.appendChild(broker_id_ele)

    user_id_ele = doc.createElement("userID")
    user_id_text = doc.createTextNode(userID)
    user_id_ele.appendChild(user_id_text)
    trader_ele.appendChild(user_id_ele)

    lastest_date = int(lastest_date_str)
    lastest_sys_id = int(lastest_sys_id_str)

    index = 0
    size = len(list_data)
    for i in xrange(0,size):
        data = list_data[i]
        date = data[3]
        sys_id = int(data[8])

        if date < lastest_date or (date == lastest_date and sys_id <= lastest_sys_id):
            continue

        if index < int(max_send_num):
            error_order_rec_ele = doc.createElement("err_order_rec%u" % (index + 1))
            trader_ele.appendChild(error_order_rec_ele)

            produce_eor_xml(doc, error_order_rec_ele, data)

            index = index + 1
        else:
            break

    result = doc.toprettyxml(indent = '')

    return (result, index)


def produce_eor_xml(doc, error_order_rec_ele, data):
    contract_ele = doc.createElement("contract")
    contract_text = doc.createTextNode(data[0])
    contract_ele.appendChild(contract_text)
    error_order_rec_ele.appendChild(contract_ele)

    ref_ele = doc.createElement("ref_id")
    ref_text = doc.createTextNode("%u" % data[8])
    ref_ele.appendChild(ref_text)
    error_order_rec_ele.appendChild(ref_ele)

    trade_date_ele = doc.createElement("trade_date")
    trade_date_text = doc.createTextNode("%u" % data[3])
    trade_date_ele.appendChild(trade_date_text)
    error_order_rec_ele.appendChild(trade_date_ele)

    trade_time_ele = doc.createElement("trade_time")
    trade_time_text = doc.createTextNode("%u" % data[4])
    trade_time_ele.appendChild(trade_time_text)
    error_order_rec_ele.appendChild(trade_time_ele)

    buy_type_ele = doc.createElement("buy_type")
    buy_type_text = doc.createTextNode(data[1])
    buy_type_ele.appendChild(buy_type_text)
    error_order_rec_ele.appendChild(buy_type_ele)

    buy_dir_ele = doc.createElement("buy_dir")
    buy_dir_text = doc.createTextNode(data[2])
    buy_dir_ele.appendChild(buy_dir_text)
    error_order_rec_ele.appendChild(buy_dir_ele)

    price_ele = doc.createElement("price")
    price_text = doc.createTextNode("%f" % data[6])
    price_ele.appendChild(price_text)
    error_order_rec_ele.appendChild(price_ele)

    number_ele = doc.createElement("number")
    number_text = doc.createTextNode("%u" % data[5])
    number_ele.appendChild(number_text)
    error_order_rec_ele.appendChild(number_ele)

    err_msg_ele = doc.createElement("error_msg")
    err_msg_text = doc.createTextNode(data[7])
    err_msg_ele.appendChild(err_msg_text)
    error_order_rec_ele.appendChild(err_msg_ele)


def SendGoodsReport(report_url, report_dir):
    if -1 == report_url.find("http://"):
        report_url = "http://" + report_url

    del_file = []
    for root,dirs,files in os.walk(report_dir):
        for filename in files:
            if filename.find("_goods.xml") != -1 and filename.find("real_goods.xml") == -1:
                fullpath = os.path.join(root,filename)
                print fullpath

                fp = open(fullpath, "rb")
                if fp:
                    result = fp.read()
                    post_report(report_url, result)
                    fp.close()

                del_file.append(fullpath)

    for fullpath in del_file:
        os.remove(fullpath)


def SendRealGoodsReport(report_url, report_dir):
    if -1 == report_url.find("http://"):
        report_url = "http://" + report_url

    del_file = []
    for root,dirs,files in os.walk(report_dir):
        for filename in files:
            if filename.find("real_goods.xml") != -1:
                fullpath = os.path.join(root,filename)
                print fullpath

                fp = open(fullpath, "rb")
                if fp:
                    result = fp.read()
                    post_report(report_url, result)
                    fp.close()

                del_file.append(fullpath)

    for fullpath in del_file:
        os.remove(fullpath)


def SendTrReport(report_url, report_dir, max_send_num):
    if -1 == report_url.find("http://"):
        report_url = "http://" + report_url

    del_file = []
    for root,dirs,files in os.walk(report_dir):
        for filename in files:
            try:
                if filename.find("trade_record.db") != -1:
                    list_file_info = filename.split('_')
                    fullpath = os.path.join(root, filename)
                    print fullpath

                    report_name_count = len(list_file_info) - 4
                    report_name = ""
                    for i in xrange(0,report_name_count):
                        if i == 0:
                            report_name = list_file_info[2+i]
                        else:
                            report_name += '_' + list_file_info[2+i]

                    result = produce_tr_set_xml(list_file_info[0], list_file_info[1], report_name, [], max_send_num, "0", "0")
                    buf = post_report(report_url, result[0])

                    result_list = read_tr_db(fullpath)
                    result_list_new = sorted(result_list, cmp=compare_tr_data)

                    while len(buf) == 16:
                        date_str = buf[0:6]
                        sys_id_str = buf[6:]

                        result = produce_tr_set_xml(list_file_info[0], list_file_info[1], report_name, result_list_new,
                            max_send_num, date_str, sys_id_str)
                        if result[1] > 0:
                            content = result[0].decode("utf8")
                            content = content.encode("gb2312")
                            buf = post_report(report_url, content)
                        else:
                            break

                    del_file.append(fullpath)
            except Exception, e:
                import traceback
                print e
                print traceback.print_exc()

    for fullpath in del_file:
        os.remove(fullpath)


def SendEorReport(report_url, report_dir, max_send_num):
    if -1 == report_url.find("http://"):
        report_url = "http://" + report_url

    del_file = []
    for root,dirs,files in os.walk(report_dir):
        for filename in files:
            try:
                if filename.find("err_order_record.db") != -1:
                    list_file_info = filename.split('_')
                    fullpath = os.path.join(root, filename)
                    print fullpath

                    report_name_count = len(list_file_info) - 5
                    report_name = ""
                    for i in xrange(0,report_name_count):
                        if i == 0:
                            report_name = list_file_info[2+i]
                        else:
                            report_name += '_' + list_file_info[2+i]

                    result = produce_eor_set_xml(list_file_info[0], list_file_info[1], report_name, [], max_send_num, "0", "0")
                    buf = post_report(report_url, result[0])

                    result_list = read_eor_db(fullpath)
                    result_list_new = sorted(result_list, cmp=compare_eor_data)

                    while len(buf) == 16:
                        date_str = buf[0:6]
                        sys_id_str = buf[6:]

                        result = produce_eor_set_xml(list_file_info[0], list_file_info[1], report_name, result_list_new,
                            max_send_num, date_str, sys_id_str)
                        if result[1] > 0:
                            content = result[0].decode("utf8")
                            content = content.encode("gb2312")
                            buf = post_report(report_url, content)
                        else:
                            break

                    del_file.append(fullpath)
            except Exception, e:
                import traceback
                print e
                print traceback.print_exc()

    for fullpath in del_file:
        os.remove(fullpath)


def SendReports(sys_info):
    SendGoodsReport(sys_info.goods_report_url, sys_info.report_dir)
    SendRealGoodsReport(sys_info.real_goods_report_url, sys_info.report_dir)
    SendTrReport(sys_info.trade_rec_report_url, sys_info.report_dir, sys_info.trade_rec_max_num)
    SendEorReport(sys_info.err_order_rec_report_url, sys_info.report_dir, sys_info.err_order_rec_max_num)


def main():
    print "Server start!", "-" * 20
    sys_info = SystemConfig("system.ini")

    SendReports(sys_info)
    last_time = time.time()
    while True:
        try:
            now = time.time()

            diff_time = (now - last_time)
            if diff_time < 10:
                time.sleep(0.1)
                continue
            print 'interval %f diff_time seconds!' % diff_time
            last_time = now

            SendReports(sys_info)

        except Exception, e:
            import traceback
            print e
            print traceback.print_exc()
            

if __name__ == '__main__':
    main()
