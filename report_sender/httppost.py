#! /usr/bin/python
# -*- coding: utf-8 -*-

import md5
import time, datetime
import httplib
import urllib

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def httpPost(url, data):
    res = None
    try:
        now = time.time()
        urlInfo = httplib.urlsplit(url)
        conn = httplib.HTTPConnection(urlInfo.netloc)
        conn.connect()

        if data:
            conn.putrequest("POST", url)
            conn.putheader("Content-Length", len(data))
            conn.putheader("Content-Type", "application/x-www-form-urlencoded")
            conn.putheader("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36")

            conn.putheader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
            conn.putheader("Accept-Encoding", "gzip, deflate, sdch")
            conn.putheader("Accept-Language", "zh-CN,zh;q=0.8")

        else:
            conn.putrequest("GET", urlInfo.path, None)
            conn.putheader("Content-Length", 0)

        conn.putheader("Connection", "close")
        conn.endheaders()

        if data:
            conn.send(data)

        response = conn.getresponse()
        if response:
            res = response.read()
            response.close()
        conn.close()
        print urlInfo.path,urlInfo.port,urlInfo.netloc,"%.3f" % (time.time() - now)
        return res
    except Exception, ex:
        import traceback
        print ex, traceback.print_exc()
        # raise ex



if __name__ == '__main__':

    postUrl = "http://wap.5656k.com/pay/payCallbackApp2.php"
    content = 'type=check&data=ewoJInNp'

    try:
        # res = httpPost(postUrl, None)
        res = httpPost(postUrl, content)

        if res is None:
            print("None")
            exit(1)

        print(res)
        with fopen("1.txt", "w+") as f:
            f.write(res)
    except Exception, e:
        print(e)

    data=urllib.urlopen(postUrl).read()
    print(data)
