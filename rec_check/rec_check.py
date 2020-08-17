import os
import re
import db
import log
import time
from datetime import date
import urllib2
import ConfigParser
import json
import sys
import requests

os.environ['REQUESTS_CA_BUNDLE'] = 'cacert.pem'
CorpID = "wx07e07f9973580429"
Secret = "o3z4KdRjj9AvHW3xLWcEFkaND8EBEpDKjLzWt-act541kYAGC8C6cQuelfCiXADW"


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


def print_log(msg):
    # 设置日志模式为追加
    log.set_log_mode('a')

    now_datetime = time.localtime()
    content = u"%u-%02u-%02u %02u:%02u:%02u %s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, now_datetime.tm_hour, 
              now_datetime.tm_min, now_datetime.tm_sec, msg)
    log.WriteLog("sys", content)


class SystemConfig(object):
    # 配置文件信息结构
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.weixin_touser = ini_parser.get("weixin", "touser")
        self.weixin_agentid = ini_parser.get("weixin", "agentid")

        self.db_host = ini_parser.get("db_fund", "host")
        self.db_user = ini_parser.get("db_fund", "user")
        self.db_password = ini_parser.get("db_fund", "password")
        self.db_db = ini_parser.get("db_fund", "db")
        self.db_port = ini_parser.getint("db_fund", "port")
        self.db_charset = ini_parser.get("db_fund", "charset")

        self.account_pairs = []
        self.account_key_infos = {}
        self.account_except_contracts = {}
        sections = ini_parser.sections()
        for section in sections:
            if section.find(":") < 0:
                continue

            self.account_key_infos[section] = {}
            self.account_pairs.append(section.split(':'))
            self.account_except_contracts[section] = []

            for i in xrange(1,100):
                key = "key%u" % i
                if not ini_parser.has_option(section, key):
                    break

                value = ini_parser.get(section, key)
                key_info = value.split(':')
                self.account_key_infos[section][key_info[0]] = (key_info[1],key_info[2])

            for i in xrange(1,100):
                key = "except%u" % i
                if not ini_parser.has_option(section, key):
                    break

                value = ini_parser.get(section, key)
                self.account_except_contracts[section].append(value)

        print self.account_except_contracts


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
            strError = u"发送出错：%s %s" % (errcode, errmsg)
            print_log(strError)


def is_exception(symbol, except_contracts):
    for except_contract in except_contracts:
        if symbol == except_contract:
            return True

    return False


def rec_check(db, account_pair, key_infos, except_contracts):
    sql = "select * from fd_report_record where `key` in (%s) and `tradeName` in (%s) order by contract desc" \
     % ((',').join("'%s'" % key for key in key_infos.keys()), (',').join("'%s'" % account for account in account_pair))
    db.Query(sql)
    recs = db.FetchAll()
    if not recs:
        err = 'query rec failed'
        raise Exception, err
        return

    rec_info = {}
    for rec in recs:
        rec_key = "%s_%s" % (rec[0], rec[2])
        if not rec_info.has_key(rec_key):
            rec_info[rec_key] = {}

        number = int(get_number(rec[1]))
        cur_date = date.today()
        cur_yymm = cur_date.year % 100 * 100 + cur_date.month
        if number < cur_yymm:
            continue

        rec_info[rec_key][rec[1]] = rec[3]

    content = ""
    for key in key_infos.keys():
        key_info = key_infos[key]
        rate = float(key_info[0])
        min_diff = float(key_info[1])

        if 0 == rate:
            continue

        rec_key1 = "%s_%s" % (account_pair[0], key)
        if not rec_info.has_key(rec_key1):
            content = content + u"账号[%s]rec记录不包含关键字[%s]\n" % (account_pair[0], key)

        rec_key2 = "%s_%s" % (account_pair[1], key)
        if not rec_info.has_key(rec_key2):
            content = content + u"账号[%s]rec记录不包含关键字[%s]\n" % (account_pair[1], key)

        if rec_info.has_key(rec_key1) and rec_info.has_key(rec_key2):
            rec_contract_info1 = rec_info[rec_key1]
            rec_contract_info2 = rec_info[rec_key2]

            for contract in rec_contract_info1.keys():
                symbol = get_symbol(contract)
                if is_exception(symbol, except_contracts):
                    continue

                if rec_contract_info2.has_key(contract):
                    rec_value1 = float(rec_contract_info1[contract]) / rate
                    rec_value2 = float(rec_contract_info2[contract]) / rate

                    if abs(rec_value1 - rec_value2) >= min_diff:
                        content = content + u"账号[%s]与[%s]在合约[%s]，关键字[%s]下的rec记录不一致 [%s]值[%s] [%s]值[%s]\n" % (
                            account_pair[0], account_pair[1], contract, key, account_pair[0], rec_value1, account_pair[1], rec_value2)

    return content


def main():
    sys_info = SystemConfig("system.ini")
    token = Token(CorpID, Secret)
    database = db.DB(host=sys_info.db_host,user=sys_info.db_user, passwd=sys_info.db_password, db=sys_info.db_db, 
        charset=sys_info.db_charset, port=sys_info.db_port)

    for account_pair in sys_info.account_pairs:
        account_pair_key = "%s:%s" % (account_pair[0], account_pair[1])
        content = rec_check(database, account_pair, sys_info.account_key_infos[account_pair_key], 
            sys_info.account_except_contracts[account_pair_key])
        if len(content) > 0:
            print_log(content)
            token.send_msg(sys_info.weixin_touser, sys_info.weixin_agentid, content.encode("utf-8"))


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        print_log(e[0])
        import traceback
        print_log(traceback.print_exc())