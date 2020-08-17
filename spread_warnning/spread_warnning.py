import db
import sys
import urllib2
import time
import json
import requests
import os
import log
import string
import ConfigParser
import datetime

# py2exe打包 后会找不到证书文件，需要将该文件放置到运行目录下
os.environ['REQUESTS_CA_BUNDLE'] = 'cacert.pem'
CorpID = "wx07e07f9973580429"
Secret = "o3z4KdRjj9AvHW3xLWcEFkaND8EBEpDKjLzWt-act541kYAGC8C6cQuelfCiXADW"
sendmsg_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s"
connect_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s"

IF_MARGIN_RATE = 0.11
IF_COMMISSION = 0.00003
FUND_COMMISSION = 0.0004
MAP_MULTIPLIER = {"IF":300,"IH":300,"IC":200}

def is_trade_time(time):
    hhmm = time%10000
    if hhmm >=930 and hhmm <= 1129: return True 
    if hhmm >=1259 and hhmm <= 1514: return True
    return False

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
        errcode = ret.json["errcode"]
        errmsg = ret.json["errmsg"]
        if errcode != 0:
            strError = "%s %s" % (errcode, errmsg)
            print_log(strError)


class MarketDetect(object):
    # 获取数据库信息，检测升贴水情况是否超过规定
    def __init__(self, host, user, password, db_name, port, charset, src_table, tar_table, spread_table):
        self.src_table = src_table
        self.tar_table = tar_table
        self.spread_table = spread_table

        self.db = db.DB(host=host, user=user, passwd=password, db=db_name, charset=charset, port=port)

        sql = "select * from %s" % self.spread_table
        self.db.Execute(sql)

        self.set_spread_info = self.db.FetchAll()

    def is_connect(self):
        return self.db.IsConnect()

    def re_connect(self):
        self.db.ReConnect()

    def calc_reward(self, instrument_id, src_price, tar_price):
        sql = "select date from `contract_expire` where `name`='%s'" % (instrument_id)
        self.db.Query(sql)
        contract_expire = self.db.FetchOne()
        expire_date = contract_expire[0]
        now_date = datetime.date.today()
        date_diff = expire_date - now_date
        if 0 == date_diff.days:
            return ""

        symbol = get_symbol(instrument_id)
        profit = abs(tar_price - src_price) * MAP_MULTIPLIER[symbol]
        total_money = src_price * MAP_MULTIPLIER[symbol] * (IF_MARGIN_RATE + 1)
        if 0 == total_money:
            return ""
        commision = src_price * MAP_MULTIPLIER[symbol] * (IF_COMMISSION * 2 + FUND_COMMISSION * 2)
        profit_net = profit - commision
        rz_cost = src_price * MAP_MULTIPLIER[symbol] * (0.086 / 365) * date_diff.days
        reward_y = (profit_net/total_money)/abs(date_diff.days) * 365 * 100
        reward_y2 = (profit_net-rz_cost)/total_money/abs(date_diff.days) * 365 * 100

        reward_content = u"利润：%d|非融资盈利率：%.2f%%|融资盈利率：%.2f%%" % (profit_net, reward_y, reward_y2)

        return reward_content

    def detect(self):
        set_out_line_info = {}
        for spread_info in self.set_spread_info:
            sql = "select Time,ClosePrice from %s where `InstrumentID`='%s' order by Time Desc limit 1" % (self.tar_table, spread_info[0])
            self.db.Query(sql)
            tar_marekt_info = self.db.FetchOne()
            tar_time = tar_marekt_info[0]
            tar_close_price = float(tar_marekt_info[1]) / 1000

            src_column_name = ""
            if spread_info[0][:2] == "IF":
                src_column_name = "sh000300"
            elif spread_info[0][:2] == "IC":
                src_column_name = "sh000905"
            elif spread_info[0][:2] == "IH":
                src_column_name = "sh000016"

            sql = "select datetime,%s from %s order by datetime Desc limit 1" % (src_column_name, self.src_table)
            self.db.Query(sql)
            src_market_info = self.db.FetchOne()
            src_time = src_market_info[0]
            src_close_price = float(src_market_info[1]) / 100

            if tar_time != src_time:
                continue

            reward_content = self.calc_reward(spread_info[0], src_close_price, tar_close_price)
            print "ddd%s" % reward_content

            diff = tar_close_price - src_close_price
            if diff > spread_info[1] and spread_info[1] > 0:
                out_line_info = [1, diff, reward_content]
                set_out_line_info[spread_info[0]] = out_line_info
            elif -diff > spread_info[2] and spread_info[2] > 0:
                out_line_info = [-1, -diff, reward_content]
                set_out_line_info[spread_info[0]] = out_line_info

        return set_out_line_info


class SystemConfig(object):
    # 配置文件信息结构
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.table_src_name = ini_parser.get("table", "src_name")
        self.table_tar_name = ini_parser.get("table", "tar_name")
        self.table_spread_name = ini_parser.get("table", "spread_name")
        self.weixin_touser = ini_parser.get("weixin", "touser")
        self.weixin_agentid = ini_parser.get("weixin", "agentid")
        self.db_host = ini_parser.get("db", "host")
        self.db_user = ini_parser.get("db", "user")
        self.db_password = ini_parser.get("db", "password")
        self.db_db = ini_parser.get("db", "db")
        self.db_port = string.atoi(ini_parser.get("db", "port"))
        self.db_charset = ini_parser.get("db", "charset")
        self.main_notice_interval = string.atoi(ini_parser.get("main", "notice_interval"))


if __name__ == '__main__':
    system_info = SystemConfig("system.ini")

    detect = MarketDetect(system_info.db_host, system_info.db_user, system_info.db_password, system_info.db_db, 
                          system_info.db_port, system_info.db_charset, system_info.table_src_name, system_info.table_tar_name, 
                          system_info.table_spread_name)

    token = Token(CorpID, Secret)

    set_last_send_time = {}
    while True:
        try:
            now = time.time()
            
            now_datetime = time.localtime()
            now_min = now_datetime.tm_hour * 100 + now_datetime.tm_min

            if is_trade_time(now_min):
                if not detect.is_connect(): detect.re_connect()

                total_content = ""
                set_out_line_info = detect.detect()
                for ins_name, out_line_info in set_out_line_info.items():
                    if not set_last_send_time.has_key(ins_name) or now - set_last_send_time[ins_name] > system_info.main_notice_interval:
                        if out_line_info[0] == 1:
                            content = u"%s升水%.2f点，%s\n" % (ins_name, out_line_info[1], out_line_info[2])
                            total_content += content
                            set_last_send_time[ins_name] = now
                        elif out_line_info[0] == -1:
                            content = u"%s贴水%.2f点, %s\n" % (ins_name, out_line_info[1], out_line_info[2])
                            total_content += content
                            set_last_send_time[ins_name] = now

                if len(total_content) > 0:
                    print_log(total_content)
                    # token.send_msg(system_info.weixin_touser, system_info.weixin_agentid, total_content.encode("utf-8"))
        except Exception, msg:
            try:
                if msg[0] == 2006:
                    detect.re_connect()
                else:
                    import traceback
                    print msg, traceback.print_exc()

                    print_log(u"try...catch出错捕获:ID[%u] 信息[%s]" % (msg[0], msg[1]))
            except Exception, msg:
                print msg

        time.sleep(1)