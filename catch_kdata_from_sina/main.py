
# coding: utf-8

# In[ ]:

import datetime
import pyetc
import pymysql
import db
import xml.etree.ElementTree as ET
import multiprocessing
import urllib.request

g_begin_date = 20160827
g_config = None


# In[ ]:

def config():
    global g_config
    if g_config is None:
        g_config = pyetc.load(r'sys.conf')
    return g_config


# In[ ]:

def get_content_from_sina(stock_id, begin_date):
    """从新浪抓取xml数据"""
    end_date = int(datetime.datetime.now().strftime('%Y%m%d'))
    params = {
        'symbol':stock_id,
        'begin_date': begin_date,
        #'end_date' : end_date
    }
    params = urllib.parse.urlencode(params)
    url = 'http://biz.finance.sina.com.cn/stock/flash_hq/kline_data.php?' + params
    data=urllib.request.urlopen(url).read()
    return data

 # import http.client, urllib.parse
 #    headers = {"Content-type": "application/x-www-form-urlencoded",
 #                "Accept": "text/plain"}
 #    conn = http.client.HTTPConnection("biz.finance.sina.com.cn")
 #    conn.request("GET", "/stock/flash_hq/kline_data.php", params, headers)
 #    response = conn.getresponse()
 #    return response.read()


# In[ ]:

def parse_sina_xml_data(data):
    """解析XML数据成HOLC数组"""
    root = ET.fromstring(data)

    vs = [{'datetime':e.attrib['d'].replace('-','') ,'open': e.attrib['o'],
        'high': e.attrib['h'], 'low': e.attrib['l'], 'close':e.attrib['c'],
        'volume': e.attrib['v']} for e in root]
    return vs


# In[ ]:

def create_database():
    conf = pyetc.load(r'sys.conf')
    mydb = db.DB(host = config().host,
             user = config().user,
             passwd = config().passwd,
             db = config().db,
             port = int(config().port),
             charset = config().charset)
    return mydb


# In[ ]:

def update2databse(database, stock_id, datas):
    """将HOLC数组更新到数据库"""
    table = config().table
    sql = "INSERT IGNORE INTO `"+table+"` VALUES(0,%s,%s,%s,%s,%s,%s,%s)"

    params = []
    for d in datas:
        params.append((stock_id, d['datetime'], d['open'], d['high'], d['low'], d['close'], d['volume']))

    try:
        database.Executemany(sql, params)
    except pymysql.err.Error as e:
        if e.args[0] != 1062:
            print(e)
            import sys,traceback
            t,v,tb = sys.exc_info()
            traceback.print_tb(tb)


# In[ ]:

def get_last_exist_date(database, stock_id):
    """获取股票最后更新日期"""
    sql = "SELECT * FROM `%s` WHERE stock_id='%s' ORDER BY datetime DESC LIMIT 1" % (config().table, stock_id)
    database.Query(sql)
    rec = database.FetchOne()
    if not rec:
        return 19900101
    return rec["datetime"]


# In[ ]:

def get_stocks_id():
    """
    获取所有股票id，并加前缀
    从东财网获取所有股票id信息，\s 替换为 \n
    http://quote.eastmoney.com/stocklist.html
    """
    f = open("stock_id.txt", "r")
    if f:
        t = f.read()
        f.close()

        import re
        r = re.compile(r'\((\d+)\)')
        gs = r.findall(t)

        stock_ids = []
        for pre in gs:
            if pre[0] == '6':
                stock_ids.append('sh%s' % pre)
            elif pre[0] == '0' or pre[0] == '3':
                stock_ids.append('sz%s' % pre)

        stock_ids.append('sh000001')
        # stock_ids.append('sh601069')
        return stock_ids


# In[ ]:

def my_proc(p):
    database = create_database()
    stock_id = p[0]
    index = p[1]
    total = p[2]
    # index = index + 1
    # 抓取数据并解析
    last_date = get_last_exist_date(database, stock_id)
    c = get_content_from_sina(stock_id, last_date)
    vs = parse_sina_xml_data(c)
    # 更新入数据库
    update2databse(database, stock_id, vs)
    print("%s is done[%d/%d]! from %s" % (stock_id, index, total, last_date))


if __name__ == '__main__':
    multiprocessing.freeze_support()

    pool = multiprocessing.Pool(processes = 4)

    database = create_database()
    stock_ids = get_stocks_id()

    total = len(stock_ids)
    index = 0
    for stock_id in stock_ids:
        index = index + 1
        pool.apply_async(my_proc, ((stock_id, index, total), ))   #维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去


    pool.close()
    pool.join()   #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    print("all done.")

