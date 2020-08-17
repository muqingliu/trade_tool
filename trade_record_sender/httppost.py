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
        urlInfo = httplib.urlsplit(url)
        #print urlInfo.path,urlInfo.port,urlInfo.netloc
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
            conn.putrequest("GET", url, None)
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
        return res
    except Exception, ex:
        raise ex


def testXM():
    postUrl = "http://wap.5656k.com/pay/payCallbackXM2.php" #接口地址
    # 拼订单提交数据
    #orderStatus=TRADE_SUCCESS&payFee=100&payTime=2013-01-06 23:16:08&productCode=01&productCount=10&productName=元宝&uid=1120310
    arr ={}
    arr['appId']       = 4886;
    arr['cpOrderId']   = 'XM5_1_20130122112511036_2'
    arr['orderId']     = '21135882513211160965'
    arr['uid']         = '192164'
    arr['productCode'] = '01'
    arr['productName'] = '元宝'
    arr['productCount']= '10'
    arr['payFee']      = '100'
    arr['payTime']     = '2013-01-22 11:25:47'
    arr['orderStatus'] = 'TRADE_SUCCESS'
    arr['cpUserInfo']  = '1,16,0'
    arr['signature']   = '86d9305fdf2afdca31561ca20007d52669c4afdb'

    res = httpPost(postUrl, urllib.urlencode(arr))
    if res is None:
        exit(1)
    print res


def testAZ():

    postUrl = "http://wap.5656k.com/pay/payCallbackXM2.php" #接口地址
    # 拼订单提交数据
    #orderStatus=TRADE_SUCCESS&payFee=100&payTime=2013-01-06 23:16:08&productCode=01&productCount=10&productName=元宝&uid=1120310
    arr ={}
    arr['appId']       = 4886;
    arr['cpOrderId']   = 'XM5_1_20130122112511036_2'
    arr['orderId']     = '21135882513211160965'
    arr['uid']         = '192164'
    arr['productCode'] = '01'
    arr['productName'] = '元宝'
    arr['productCount']= '10'
    arr['payFee']      = '100'
    arr['payTime']     = '2013-01-22 11:25:47'
    arr['orderStatus'] = 'TRADE_SUCCESS'
    arr['cpUserInfo']  = '1,16,0'
    arr['signature']   = '86d9305fdf2afdca31561ca20007d52669c4afdb'

    res = httpPost(postUrl, urllib.urlencode(arr))
    if res is None:
        exit(1)
    print res


def testPay(receiverID, card_num, card_pwd):

    postUrl = "http://test.ongate.vn/OncashDeposit/TopupOnCash.asmx" #接口地址
    arr ={}
    arr['PartnerCode'] = 4886;
    arr['CARDNAME'] = 'VINACARD' # ONCASH  | VINACARD | MOBICARD | VIETTELCARD
    arr['TransID'] = '21135882513211160965' # 我方订单号
    arr['receiverID'] = receiverID
    arr['ssoToken'] = ''
    arr['serverID'] = '1'
    arr['gameID'] = '1'
    arr['gameDesc'] = '飘渺游服'
    arr['CardSerial'] = card_num
    arr['PinCodeBase64'] = card_pwd
    arr['ClientIP']  = '192.168.1.1'
    arr['BrowserInfo'] = '1'
    arr['Description'] = 'nothing'

    partnerCode = 'pdtgmb@vdc'
    partnerUserName = 'pdtgmobile'
    partnerPassword = '123456'


    Signature = md5(partnerUserName + partnerPassword + partnerCode + receiverID + TransID + UPPER_MD5(PinCodeClearText));

    arr['Signature'] = ''

    res = httpPost(postUrl, urllib.urlencode(arr))
    if res is None:
        exit(1)
    print res

def testGetSoTokenCode(receiverID):

    global partnerCode
    global partnerUserName
    global partnerPassword

    postUrl = "http://test.ongate.vn/OnGate_Channelling/Service.asmx?op=GetSSOTokenCode_New"

    arr ={}
    arr['partnerID'] = partnerCode;
    arr['customerID'] = receiverID
    arr['clientIP'] = '192.168.1.1'

    signature = md5.md5(partnerUserName + partnerPassword + partnerCode + receiverID)

    arr['signature'] = signature

    res = httpPost(postUrl, urllib.urlencode(arr))
    if res is None:
        exit(1)
    print res


if __name__ == '__main__':

    content = {}
    #postUrl = "localhost/eiyusp/passport/regist?sid="
    content["data"]= {'password':'p42544','username':'a8n0msq4'}

    # content = "p0_Cmd=ChargeCardDirect&p1_MerId=10003412494&p2_Order=Yeepay15_53_20140822180727050_20&p3_Amt=200&p4_verifyAmt=true&p5_Pid=dy&p6_Pcat=&p7_Pdesc=&p8_Url=http://wap.5656k.com/pay/paycallback.php&pa_MP=117.185.4.112,pmsj20&pa7_cardAmt=200&pa8_cardNo=42856888525582585&pa9_cardPwd=425555845655554&pd_FrpId=SZX&pr_NeedResponse=1&hmac=a2f7447ad4d67496cbc6b748fe5ec30b&pz_userId=855567&pz1_userRegTime=2014-08-22 18:07:27"
    postUrl = "http://www.5656k.com" #"http://localhost/eiyusp/passport/register?sid="

    try:
        res = httpPost(postUrl, urllib.urlencode(content))

        if res is None:
            exit(1)

        print res
    except Exception, e:
        print(e)
 