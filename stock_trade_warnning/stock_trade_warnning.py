import time
import urllib2
import json
import requests
import sys
import os
import log
import string
import threading
from datetime import datetime,timedelta
import exchange_config
import ConfigParser
import xml.dom.minidom
import httppost
import shutil

# py2exe打包 后会找不到证书文件，需要将该文件放置到运行目录下
os.environ['REQUESTS_CA_BUNDLE'] = 'cacert.pem'
CorpID = "wx07e07f9973580429"
Secret = "o3z4KdRjj9AvHW3xLWcEFkaND8EBEpDKjLzWt-act541kYAGC8C6cQuelfCiXADW"
set_last_send_time = {}

def add_min(minute, diff_mins):
    datetime_cur = datetime(2000 + minute/100000000, minute / 1000000 % 100, minute / 10000 % 100, minute / 100 % 100, minute % 100)
    datetime_next = datetime_cur + timedelta(minutes = diff_mins)
    minute_next = datetime_next.year % 100 * 100000000 + datetime_next.month * 1000000 + datetime_next.day * 10000 + datetime_next.hour * 100 + datetime_next.minute

    return minute_next

def is_trade_time(now_datetime, set_timearea, set_holiday, is_day):
    if now_datetime.tm_wday == 6:
        return False

    date = now_datetime.tm_year % 100 * 10000 + now_datetime.tm_mon * 100 + now_datetime.tm_mday
    for holiday in set_holiday:
        if holiday == date:
            return False

    minute = now_datetime.tm_year % 100 * 100000000 + now_datetime.tm_mon * 1000000 + now_datetime.tm_mday * 10000 + now_datetime.tm_hour * 100 + now_datetime.tm_min
    minute_next_date = add_min(minute, 1440)
    minute_prev_date = add_min(minute, -1440)
    next_date = minute_next_date / 10000
    prev_date = minute_prev_date / 10000

    is_next_date_holiday = False
    for holiday in set_holiday:
        if next_date == holiday:
            is_next_date_holiday = True
            break

    is_prev_date_holiday = False
    for holiday in set_holiday:
        if prev_date == holiday:
            is_prev_date_holiday = True
            break

    hhmm = now_datetime.tm_hour * 100 + now_datetime.tm_min
    for timearea in set_timearea:
        if hhmm >= timearea[0] and hhmm < timearea[1]:
            if is_next_date_holiday and timearea[0] / 100 == 21:
                return False
            # 周六的话只有0000-0230这段时间是有效交易时间
            elif now_datetime.tm_wday == 5 and timearea[0] != 0:
                return False
            # 周一或节假日后的第一个工作日的0000-0230无效
            elif (now_datetime.tm_wday == 0 or is_prev_date_holiday) and timearea[0] == 0:
                return False
            elif is_day and (timearea[0] / 100 == 21 or timearea[0] == 0):
                return False

            return True

    return False

def print_log(msg):
    # 设置日志模式为追加
    log.set_log_mode('a')

    now_datetime = time.localtime()
    content = u"%u-%02u-%02u %02u:%02u:%02u %s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, now_datetime.tm_hour, 
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

def get_url_info(url):
    res = httppost.httpPost(url, "")
    if res is None:
        return {}

    url_info = json.loads(res)

    return url_info

def check_xml(info):
    try:
        now_datetime = time.localtime()
        content = u"%u-%02u-%02u %02u:%02u:%02u 遍历文件检测"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, 
            now_datetime.tm_hour, now_datetime.tm_min, now_datetime.tm_sec)
        print(content)

        system_info = info[0]
        url_info = info[1]
        holiday_info = info[2]
        exchange_info = info[3]

        now_min = now_datetime.tm_hour * 100 + now_datetime.tm_min

        xml_parser = XmlParser(system_info.main_xml_dir)
        set_account_info = xml_parser.Parser()

        total_content = ""
        for name, account_info in set_account_info.items():
            if not url_info.has_key(name):
                continue

            if is_trade_time(now_datetime, system_info.set_timearea, holiday_info.set_holiday, url_info[name] == 1):
                # print name, account_info
                last_inited_key = "%s_inited" % name
                last_main_time_key = "%s_main_time" % name
                if 0 == account_info["inited"]:
                    if not set_last_send_time.has_key(last_inited_key) or now - set_last_send_time[last_inited_key] > system_info.main_notice_interval:
                        content = u"%s未初始化成功\n" % (name)
                        total_content += content
                        set_last_send_time[last_inited_key] = now
                elif now - account_info["main_time"] > system_info.main_offline_limit:
                    if not set_last_send_time.has_key(last_main_time_key) or now - set_last_send_time[last_main_time_key] > system_info.main_notice_interval:
                        now_st = datetime.fromtimestamp(now)
                        main_time_st = datetime.fromtimestamp(account_info["main_time"])
                        now_min_str = ("%02u%02u%02u%02u%02u%02u") % (now_st.year%100,now_st.month,now_st.day,now_st.hour,now_st.minute,now_st.second)
                        main_time_min_str = ("%02u%02u%02u%02u%02u%02u") % (main_time_st.year%100,main_time_st.month,main_time_st.day,main_time_st.hour,main_time_st.minute,main_time_st.second)

                        content = u"%s断线，当前：%s 登记：%s\n" % (name, now_min_str, main_time_min_str)
                        total_content += content
                        set_last_send_time[last_main_time_key] = now
                else:
                    for key, info in account_info.items():
                        if cmp(key, "inited") == 0 or cmp(key, "main_time") == 0:
                            continue

                        symbol = get_symbol(info[0])
                        last_time_key = "%s_%s" % (name, key)
                        if now - info[1] > system_info.main_offline_limit and exchange_info.is_in_exchange_time(symbol, now_min):
                            if not set_last_send_time.has_key(last_time_key) or now - set_last_send_time[last_time_key] > system_info.main_notice_interval:
                                now_st = datetime.fromtimestamp(now)
                                info_st = datetime.fromtimestamp(info[1])
                                now_min_str = ("%02u%02u%02u%02u%02u%02u") % (now_st.year%100,now_st.month,now_st.day,now_st.hour,now_st.minute,now_st.second)
                                info_min_str = ("%02u%02u%02u%02u%02u%02u") % (info_st.year%100,info_st.month,info_st.day,info_st.hour,info_st.minute,info_st.second)

                                content = u"%s合约%s断线，当前：%s 登记：%s\n" % (name, info[0], now_min_str, info_min_str)
                                total_content += content
                                set_last_send_time[last_time_key] = now

                                #当出现断线情况时，记录断线时的文件情况
                                filename = "%s.xml" % name

                                new_file = u"exception/%u-%02u-%02u-%02u-%02u-%02u-%s"%(now_datetime.tm_year, now_datetime.tm_mon, 
                                    now_datetime.tm_mday, now_datetime.tm_hour, now_datetime.tm_min, now_datetime.tm_sec, filename)

                                tar_file_path = os.path.join(system_info.main_xml_dir, filename)
                                print tar_file_path
                                shutil.copyfile(tar_file_path, new_file) 

        if len(total_content) > 0:
            print_log(total_content)
            token.send_msg(system_info.weixin_touser, system_info.weixin_agentid, total_content.encode("utf-8"))
    except Exception, msg:
        import traceback
        print_log(u"判断断线问题过程出错，错误信息：%s" % (msg))
        print msg, traceback.print_exc()


class Token(object):
    # 获取token
    def __init__(self, corpid, corpsecret):
        self.baseurl = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}'.format(corpid, corpsecret)
        self.expire_time = 0

    def get_token(self):
        if self.expire_time < time.time():
            request = urllib2.Request(self.baseurl)
            response = urllib2.urlopen(request)
            ret = response.read().strip()
            ret = json.loads(ret)
            if 'errcode' in ret.keys():
                strError = "%s %s" % (ret['errmsg'], sys.stderr)
                print_log(strError)
            self.expire_time = time.time() + ret['expires_in']
            self.access_token = ret['access_token']
        return self.access_token

    def send_msg(self, user, agentid, content):
        # 发送消息

        # print qs_token
        qs_token = self.get_token()
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(qs_token)

        payload = {
            "msgtype": "text",
            "text": {
                "content": "{0}".format(content)
            },
            "safe": "0"
        }
        payload["touser"] = user
        payload["agentid"] = agentid

        ret = requests.post(url, data=json.dumps(payload, ensure_ascii=False))
        errcode = ret.json()["errcode"]
        errmsg = ret.json()["errmsg"]
        if errcode != 0:
            strError = "发送出错：%s %s" % (errcode, errmsg)
            print_log(strError)


class SystemConfig(object):
    # 配置文件信息结构
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.set_timearea = []
        time_begin = 0
        time_end = 0
        count = 1
        for option in ini_parser.options("timearea"):
            template_begin = "time_begin%u" % count
            template_end = "time_end%u" % count
            if cmp(option, template_begin) == 0:
                time_begin = ini_parser.getint("timearea", option)
            elif cmp(option, template_end) == 0:
                time_end = ini_parser.getint("timearea", option)
                self.set_timearea.append([time_begin, time_end])
                count = count + 1

        self.weixin_touser = ini_parser.get("weixin", "touser")
        self.weixin_agentid = ini_parser.get("weixin", "agentid")
        self.main_xml_dir = ini_parser.get("main", "xml_dir")
        self.main_offline_limit = string.atoi(ini_parser.get("main", "offline_limit"))
        self.main_notice_interval = string.atoi(ini_parser.get("main", "notice_interval"))
        self.main_url = ini_parser.get("main", "url")


class HolidayInfo(object):
    """docstring for HolidayInfo"""
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.set_holiday = []
        for option in ini_parser.options("holiday"):
            holiday = ini_parser.getint("holiday", option)
            self.set_holiday.append(holiday)


class XmlParser(object):
    # Xml文件检查器
    def __init__(self, path):
        self.set_dom = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                try:
                    name = ""
                    ext = ""
                    index = filename.find('.')
                    if index != -1:
                        name = filename[:index]
                        ext = filename[index + 1:]

                    if len(name) == 0 or ext != "xml":
                        continue

                    tar_file_path = os.path.join(root, filename)
                    dom = xml.dom.minidom.parse(tar_file_path)

                    self.set_dom.append([name, dom])
                except Exception, msg:
                    # now_datetime = time.localtime()
                    # new_file = u"exception/%u-%02u-%02u-%02u-%02u-%02u-%s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, 
                    #             now_datetime.tm_hour, now_datetime.tm_min, now_datetime.tm_sec, filename)

                    # tar_file_path = os.path.join(root, filename)
                    # print tar_file_path
                    # shutil.copyfile(tar_file_path, new_file) 
                    import traceback
                    print_log(u"解析%s文件出错，错误信息：%s" % (filename, msg))
                    print traceback.print_exc()

        self.set_account_info = {}

    def Parser(self):
        for file_name, dom in self.set_dom:
            try:
                account_info = {}

                root = dom.documentElement

                set_time_ele = root.getElementsByTagName("time")
                main_time = set_time_ele[0].firstChild.data
                account_info["main_time"] = string.atoi(main_time)

                set_inited_ele = root.getElementsByTagName("inited")
                inited = set_inited_ele[0].firstChild.data
                account_info["inited"] = string.atoi(inited)

                set_contract_ele = root.getElementsByTagName("contract")
                index = 1
                for contract_ele in set_contract_ele:
                    contract = contract_ele.firstChild.data
                    goods_time = string.atoi(set_time_ele[index].firstChild.data)

                    key = "time%u" % index
                    account_info[key] = [contract, goods_time]

                    index = index + 1

                self.set_account_info[file_name] = account_info
            except Exception, msg:
                import traceback
                print_log(u"解析%s文件出错，错误信息：%s" % (file_name, msg))
                print traceback.print_exc()

        return self.set_account_info


if __name__ == '__main__':
    print_log(u"警报工具启动...")

    if not os.path.exists("exception"):
        os.mkdir("exception")

    system_info = SystemConfig("system.ini")
    holiday_info = HolidayInfo("holiday.ini")
    exchange_info = exchange_config.exchange_config("exchange.ini")
    url_info = get_url_info(system_info.main_url)

    for root, dirs, files in os.walk(system_info.main_xml_dir):
        for name in files:
            print(name)

    info = []
    info.append(system_info)
    info.append(url_info)
    info.append(holiday_info)
    info.append(exchange_info)
    # info["system"] = system_info
    # info["url"] = url_info
    # info["holiday"] = holiday_info
    # info["exchange"] = exchange_info
            
    token = Token(CorpID, Secret)

    last_time = 0
    set_thread = []
    while True:
        now = time.time()
        if now - last_time < 60:
            time.sleep(1)
            continue

        thread_count = len(set_thread)
        alive_count = 0
        set_del_index = []
        for i in xrange(0,thread_count):
            old_t = set_thread[i]
            if old_t.isAlive():
                alive_count = alive_count + 1
            else:
                set_del_index.append(i)

        if alive_count > 0:
            print_log(u"有%u条线程未曾运行完毕" % alive_count)

        del_thread_count = len(set_del_index)
        for i in xrange(0,del_thread_count):
            del_index = set_del_index[del_thread_count - 1 - i]
            del set_thread[del_index]

        t = threading.Thread(target=check_xml, args=[info])
        t.setDaemon(True)
        t.start()

        set_thread.append(t)

        last_time = time.time()

        time.sleep(1)