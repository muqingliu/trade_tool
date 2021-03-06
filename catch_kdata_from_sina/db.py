﻿
import pymysql
#from common import func
#from common import log
import time


class DB(object):

    cursor = None
    conn = None
    table_name = None

    def __init__(this, host, user, passwd, db, table='', charset='gbk', port=3306):
        this.host = host
        this.user = user
        this.passwd = passwd
        this.db = db
        this.table_name = table
        this.charset = charset
        this.port = port
        this.__connect()

    def __connect(this):
        try:
            # this.conn = MySQLdb.connect(this.host, this.user, this.passwd, this.db, this.port, charset=this.charset)
            this.conn = pymysql.connect(
                host=this.host, port=this.port, user=this.user, passwd=this.passwd, db=this.db, charset=this.charset)
            this.cursor = this.conn.cursor(pymysql.cursors.DictCursor)
            this.cursor.execute("SET NAMES %s" % this.charset)
        except Exception as msg:
            print(msg)
            #log.WriteError('Error: cant connect db names %s from host %s %s' % (#this.db, this.host, msg))

    def IsConnect(this):
        return this.conn != None

    def query(this, sql):
        this.conn.query(sql)

    def ReConnect(this):
        this.__connect()

    def Query(this, sql, *the_tuple):
        time_begin = time.time()
        if(len(the_tuple)>0):
            this.cursor.execute(sql % the_tuple)
        else:
            this.cursor.execute(sql)
        # print("time:%d SQL[%s]" % ((time.time()-time_begin), sql % the_tuple))

    def Execute(this, sql, *the_tuple):
        if the_tuple:
            return this.cursor.execute(sql, the_tuple)
        else:
            return this.cursor.execute(sql)
        # this.Commit()

    def Executemany(this, sqls, params):
        this.cursor.executemany(sqls, params)
        # this.conn.commit()

    def Commit(this):
        this.conn.commit()

    # row object
    def FetchOne(this):
        return this.cursor.fetchone()

    def FetchOne_1_Col(this):
        return this.FetchOne()[0]

    # list of row object
    def FetchAll(this):
        return this.cursor.fetchall()

    def StoreResult(this):
        return this.conn.store_result()

    def __del__(this):
        if this.conn:
            this.cursor.close()
            this.conn.close()


def iterate_DB(call_back, adb, condition='', user_data=None, rows_once=6000, limit=0):
    # iterate all rows of db:
    if not adb or not adb.IsConnect():
        return

    sql = 'SELECT COUNT(0) FROM %s %s' % (adb.table_name, condition)
    adb.Query(sql)
    cnt = adb.FetchOne_1_Col()

    if limit:
        cnt = min(cnt, limit)
        rows_once = cnt

    if cnt < rows_once:
        rows_once = cnt

    for offset in func.range_step(0, cnt, rows_once):
        sql = 'SELECT * FROM %s %s LIMIT %u OFFSET %u' % (
            adb.table_name, condition, rows_once, offset)
        result = adb.Query(sql)

        row = adb.FetchOne()
        while(row):
            if user_data:
                if not call_back(row, user_data):
                    return
            else:
                if not call_back(row):
                    return

            row = adb.FetchOne()
