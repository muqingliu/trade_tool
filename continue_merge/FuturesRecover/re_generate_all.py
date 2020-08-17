# -*- coding: utf-8 -*-
import time
import config.config as config
import fileIO
import log
import common.func as func


def recInstruments(recoveredlist, closeprice):
    log.WriteLog('LOG_TRADE', "[===adjust===] getlast 1: Time = %s InstrumentID = %s ClosePrice = %s "
                 % (recoveredlist[-1]['Time'], recoveredlist[-1]['InstrumentID'], recoveredlist[-1]['ClosePrice']))
    ndiff = closeprice - recoveredlist[-1]['ClosePrice']
    log.WriteLog('LOG_TRADE', "[get adjusted value :]  nClosePrice - lClosePrice = %s - %s  = %s "
                 % (closeprice, recoveredlist[-1]['ClosePrice'], ndiff))

    for res in recoveredlist:
        res['HighestPrice'] = res['HighestPrice'] + ndiff
        res['OpenPrice'] = res['OpenPrice'] + ndiff
        res['LowestPrice'] = res['LowestPrice'] + ndiff
        res['ClosePrice'] = res['ClosePrice'] + ndiff

    log.WriteLog('LOG_TRADE', "[===adjusted===] getlast 1: Time = %s InstrumentID = %s ClosePrice = %s "
                 % (recoveredlist[-1]['Time'], recoveredlist[-1]['InstrumentID'], recoveredlist[-1]['ClosePrice']))

    return recoveredlist


#获得Instrument_details 表数据，具体合约基本信息
def get_insdetails(instrumentsname, mydb):

        log.WriteLog('LOG_TRADE', "==gen_all_begin instrument_info== %s" % instrumentsname)
        sql = "select InstrumentsName,Period,BeginTime from Instrument_details where InstrumentsName = '%s' " % (instrumentsname)
        log.WriteLog('LOG_TRADE', "SELECT SQL_Instrument_details :%s" % (sql))
        mydb.Execute(sql)
        instrument_details = mydb.FetchAll()

        if instrument_details == None:
            log.WriteLog('LOG_ERROR', "==instrument_details none== ")
        return instrument_details


# 获取源数据
def get_Instrument_data(instrument_info, mydb):
    for row in instrument_info:
        sourcelist = []
        recoveredlist = []
        instrument_details = get_insdetails(row['InstrumentsName'], mydb)

        if instrument_details == None:
            return

        cnt = len(instrument_details)
        for i in range(0, cnt):
            # 结束时间以下条记录开始时间为准，如果是最后一条，以当前时间为结束时间
            endtime = time.strftime('%y%m%d', time.localtime())
            if i < cnt - 1:
                endtime = instrument_details[i + 1]['BeginTime']

            # ===测试数据===
                if row['InstrumentsName'] == 'TF':
                    endtime = '140612'
                else:
                    endtime = '140616'
            # ===测试数据===

            # 构造sql查询参数
            begintime = instrument_details[i]['BeginTime'] + config.CON_BEGINTIME
            endtime = endtime + config.CON_ENDTIME
            log.WriteLog('LOG_TRADE', "[Ready GET] InstrumentsName : %s,Period : %s,BeginTime : %s,EndTime : %s" % (
                instrument_details[i]['InstrumentsName'], instrument_details[i]['Period'], instrument_details[i]['BeginTime'], endtime))
            instrumentID = instrument_details[i]['InstrumentsName'] + instrument_details[i]['Period']
            sql = """select `id`,`InstrumentID`,`Time`,`OpenPrice`,`ClosePrice`,`HighestPrice`,`LowestPrice`,`Volume`
            from %s where InstrumentID  = \"%s\" AND %s.Time+0 BETWEEN %s AND %s ORDER BY  %s.Time ASC"""% (row['Exchange'], instrumentID, row['Exchange'], begintime, endtime, row['Exchange'])

            log.WriteLog('LOG_TRADE', "SELECT SQL :%s" % (sql))
            mydb.Execute(sql)

            # 查找到源数据
            res = mydb.FetchAll()
            if res == None:
                log.WriteLog('LOG_ERROR', "instrumentID: %s isNone,begintime:%s, endtime:%s" % (instrumentID, begintime, endtime))
                return
            log.WriteLog('LOG_TRADE', "[SQL GET] SQL_Cnt :%s" % (len(res)))

            if len(recoveredlist) > 0:
                # 复权时间
                lasttime = recoveredlist[-1]['Time']
                log.WriteLog(
                    'LOG_TRADE', "[get_current_period before adjust %s]" % (instrumentID))
                sql = "select ClosePrice from %s where InstrumentID  = '%s' AND %s.Time <= %s ORDER BY  %s.Time DESC limit 1" % (
                    row['Exchange'], instrumentID, row['Exchange'], lasttime, row['Exchange'])
                mydb.Execute(sql)
                log.WriteLog('LOG_TRADE', "SELECT SQL :%s" % (sql))
                nClosePrice = mydb.FetchOne()['ClosePrice']
                log.WriteLog('LOG_TRADE', "nClosePrice = %s" % (nClosePrice))
                recoveredlist = recInstruments(recoveredlist, nClosePrice)

            for r in res:
                sourcelist.append(r)
                recoveredlist.append(r.copy())

        nmode = 1         # nmode 0:增量 1：全
        fileIO.filewrite(row['InstrumentsName'], "source", sourcelist, nmode)
        fileIO.filewrite(row['InstrumentsName'], "recover", recoveredlist, nmode)
        func.insertDB_Instruments(instrument_details[i]['InstrumentsName'], sourcelist, recoveredlist, mydb)


def re_generate_all():

    mydb = func.create_database()
    _sql = "TRUNCATE TABLE future_redetails"
    mydb.Execute(_sql)

    # 查询合约-交易所信息表
    mydb.Execute("select InstrumentsName,Exchange from instrument_info")
    instrument_info = mydb.FetchAll()

    get_Instrument_data(instrument_info, mydb)

    log.close_all()

log.set_log_mode('a')
re_generate_all()
