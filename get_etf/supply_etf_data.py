from common import db
from common import log
import basefunc

def create_db():
    db_info = {
        'host'         : 'www.5656k.com',
        'user'         : 'stock',
        'password'     : 'P)O(I*U&Y^',
        'db'         : 'stock',
        'port'      : 3308
    }

    db = basefunc.create_database(db_info)

    return db

def sql_producer(db):
    etf_data = [0,0,0,0,0,0,0,0,0]
    sql = "select * from new_etf_data where datetime > 1804181459 and datetime < 1804200947 order by datetime"
    db.Query(sql)
    recs = db.FetchAll()
    if recs and len(recs) > 0:
        for rec in recs:
            if etf_data[0] != rec[1] and etf_data[0] != 0:
                sql = "replace into etf_data value(%u,%u,%u,%u,%u,%u,%u,%u,%u)" % (etf_data[0],etf_data[1],etf_data[2],etf_data[3],
                    etf_data[4],etf_data[5],etf_data[6],etf_data[7],etf_data[8])
                log.WriteLog("sql", sql)
            etf_data[0] = rec[1]

            contract = rec[0]
            if contract == 'sh000300':
                etf_data[1] = int(rec[5] * 100)
            elif contract == 'sh510300':
                etf_data[2] = int(rec[5] * 10000)
            elif contract == 'sz159919':
                etf_data[3] = int(rec[5] * 10000)
            elif contract == 'sh510500':
                etf_data[4] = int(rec[5] * 10000)
            elif contract == 'sz159922':
                etf_data[5] = int(rec[5] * 10000)
            elif contract == 'sh510050':
                etf_data[6] = int(rec[5] * 10000)
            elif contract == 'sh000905':
                etf_data[7] = int(rec[5] * 100)
            elif contract == 'sh000016':
                etf_data[8] = int(rec[5] * 100)

        sql = "replace into etf_data value(%u,%u,%u,%u,%u,%u,%u,%u,%u)" % (etf_data[0],etf_data[1],etf_data[2],etf_data[3],
            etf_data[4],etf_data[5],etf_data[6],etf_data[7],etf_data[8])
        log.WriteLog("sql", sql)

if __name__ == '__main__':
    db = create_db()
    sql_producer(db)
