
import MySQLdb
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
            this.conn = MySQLdb.connect(this.host, this.user, this.passwd, this.db, this.port, charset=this.charset)
            this.cursor = this.conn.cursor()
            # this.cursor.execute("SET NAMES %s" % this.charset)
        except Exception, msg:
            # log.WriteError ('Error: cant connect db names %s from host %s %s' % (this.db, this.host, msg) )
            print('Error: cant connect db names %s from host %s %s' % (this.db, this.host, msg) )

    def IsConnect(this):
        return this.conn != None

    def ReConnect(this):
        this.__connect()

    def Query(this, sql, *the_tuple):
        time_begin = time.time()
        this.cursor.execute(sql % the_tuple)
        # print "time:%d SQL[%s]" % ((time.time()-time_begin), sql % the_tuple)

    def Execute(this, sql, *the_tuple):
        if the_tuple:
            return this.cursor.execute(sql, the_tuple)
        else:
            return this.cursor.execute(sql)
        #this.Commit()

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

    #list of row object
    def FetchAll(this):
        return this.cursor.fetchall()

    def StoreResult(this):
        return this.conn.store_result()

    def __del__(this):
        if this.conn:
            this.cursor.close()
            this.conn.close()
