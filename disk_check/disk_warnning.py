import time
import urllib2
import json
import requests
import sys
import os
import log
import string
import ConfigParser
import wmi

# py2exe打包 后会找不到证书文件，需要将该文件放置到运行目录下
os.environ['REQUESTS_CA_BUNDLE'] = 'cacert.pem'
CorpID = "wx07e07f9973580429"
Secret = "o3z4KdRjj9AvHW3xLWcEFkaND8EBEpDKjLzWt-act541kYAGC8C6cQuelfCiXADW"

def print_log(msg):
    # 设置日志模式为追加
    log.set_log_mode('a')

    now_datetime = time.localtime()
    content = u"%u-%u-%u %u:%u:%u %s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, now_datetime.tm_hour, 
              now_datetime.tm_min, now_datetime.tm_sec, msg)
    log.WriteLog("sys", content)

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
            strError = "%s %s" % (errcode, errmsg)
            print_log(strError)

class SystemConfig(object):
    # 配置文件信息结构
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.weixin_touser = ini_parser.get("weixin", "touser")
        self.weixin_agentid = ini_parser.get("weixin", "agentid")
        self.main_name = ini_parser.get("main", "name")
        self.main_limit_space = ini_parser.getint("main", "limit_space")
        self.main_notice_interval = ini_parser.getint("main", "notice_interval")

def disk_check():
    print("running...")

    system_info = SystemConfig("system.ini")

    token = Token(CorpID, Secret)

    last_send_time = 0
    while True:
        now = time.time()

        if now - last_send_time > system_info.main_notice_interval:
            total_content = u"服务器:%s\n" % (system_info.main_name.decode("gbk"))
            notice_msg = ""
            c = wmi.WMI()
            for physical_disk in c.Win32_DiskDrive():
                for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
                    for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                        size_mb = int(logical_disk.FreeSpace) / 1024 / 1024
                        print logical_disk.Caption,logical_disk.FreeSpace,size_mb
                        if size_mb < system_info.main_limit_space:
                            content = u"%s盘剩余空间不足%.2fGB\n" % (logical_disk.Caption, float(system_info.main_limit_space) / 1024)
                            notice_msg = notice_msg + content

            if len(notice_msg) > 0:
                total_content = total_content + notice_msg
                print_log(total_content)
                token.send_msg(system_info.weixin_touser, system_info.weixin_agentid, total_content.encode("utf-8"))

            last_send_time = now

        time.sleep(1)

if __name__ == '__main__':
	disk_check()