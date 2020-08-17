import time
import config.config as config
import fileIO
import log
import common.func as func


def con_gentodate(sourcelist, recoveredlist, lpara, mydb):
    sql = """select `Time`,`rOpenPrice` as OpenPrice,`rClosePrice` as ClosePrice,`rHighestPrice` as HighestPrice,`rLowestPrice` as LowestPrice, `Volume`
    from future_redetails where InstrumentsName = '%s'"""% lpara['InstrumentsName']
    mydb.Execute(sql)
    reclist = mydb.FetchAll()
    fileIO.filewrite(lpara['InstrumentsName'], "recover", reclist, 1)
    fileIO.filewrite(lpara['InstrumentsName'], "source", sourcelist, 0)
    fileIO.filewrite(lpara['InstrumentsName'], "recover", recoveredlist, 0)
    func.insertDB_Instruments(
        lpara['InstrumentsName'], sourcelist, recoveredlist, mydb)


# 复权操作
def rec_closePrice(mydb, tlist, recoveredlist):
    if len(recoveredlist) > 0:
        endtime = recoveredlist[-1]['Time']
    else:
        endtime = tlist['BeginTime'] + config.CON_ENDTIME
    InstrumentID = tlist['InstrumentsName'] + tlist['Period']

    log.WriteLog('LOG_TRADE', "[get_current_period before adjust %s]" % (InstrumentID))

    sql = """select ClosePrice from %s where InstrumentID
    = \"%s\" AND %s.Time <= %s ORDER BY  %s.Time DESC limit 1"""% (tlist['Exchange'], InstrumentID, tlist['Exchange'], endtime, tlist['Exchange'])
    log.WriteLog('LOG_TRADE', "SELECT SQL :%s" % (sql))
    mydb.Execute(sql)

    lcloseprice = mydb.FetchOne()
    if lcloseprice == None:
        log.WriteLog('LOG_ERROR', "getlastClosePrice = None")
        return

    rncloseprice = lcloseprice['ClosePrice']
    log.WriteLog('LOG_TRADE', "nClosePrice = %s" % (rncloseprice))
    if len(recoveredlist) <= 0:
         # 得到当期收盘价
        ndiff = rncloseprice - tlist['nClosePrice']
        log.WriteLog('LOG_TRADE', "[get adjusted value :]  closeprice - rncloseprice = %s - %s  = %s " % (
            rncloseprice, tlist['nClosePrice'], ndiff))
    else:
        closeprice = recoveredlist[-1]['ClosePrice']
        ndiff = rncloseprice - closeprice
        log.WriteLog('LOG_TRADE', "[get adjusted value :]  closeprice - rncloseprice = %s - %s  = %s " % (
            rncloseprice, recoveredlist[-1]['ClosePrice'], ndiff))
        for r in recoveredlist:
            r['HighestPrice'] = r['HighestPrice'] + ndiff
            r['OpenPrice'] = r['OpenPrice'] + ndiff
            r['LowestPrice'] = r['LowestPrice'] + ndiff
            r['ClosePrice'] = r['ClosePrice'] + ndiff

    # 对历史数据update
    sql = "update future_redetails set rClosePrice = rClosePrice + %s,rHighestPrice = rHighestPrice + %s,rLowestPrice = rLowestPrice + %s,rOpenPrice = rOpenPrice + %s where InstrumentsName = '%s'" % (
        ndiff, ndiff, ndiff, ndiff, tlist['InstrumentsName'])
    log.WriteLog('LOG_TRADE', "update SQL :%s" % (sql))
    mydb.Execute(sql)

    return recoveredlist


def get_hq_data(mydb, tlist):
    reslist = []
    # 构造sql查询参数
    begintime = str(tlist['BeginTime']) + config.CON_BEGINTIME
    endtime = tlist['Endtime'] + config.CON_ENDTIME
    InstrumentID = tlist['InstrumentsName'] + tlist['Period']

    sql = "select `id`,`InstrumentID`,`Time`,`OpenPrice`,`ClosePrice`,`HighestPrice`,`LowestPrice`,`Volume` from %s where InstrumentID  = \"%s\" AND %s.Time+0 BETWEEN %s AND %s ORDER BY  %s.Time ASC" % (
        tlist['Exchange'], InstrumentID, tlist['Exchange'], begintime, endtime, tlist['Exchange'])
    log.WriteLog('LOG_TRADE', "SELECT SQL :%s" % (sql))
    mydb.Execute(sql)
    # 查找到源数据
    res = mydb.FetchAll()

    for r in res:
        reslist.append(r)
    log.WriteLog('LOG_TRADE', "[SQL GET] SQL_Cnt :%s" % (len(res)))
    return reslist

# 通过数据库最后一条记录重新配置Instrument_details


def reset_Instrument_details(mydb, row):
    sql = "select InstrumentsName,Period,BeginTime from Instrument_details where InstrumentsName =  '%s'" % row['InstrumentsName']
    mydb.Execute(sql)
    instrument_details = mydb.FetchAll()

    sql = "select `Time`,`rClosePrice` from future_redetails where InstrumentsName =  '%s' ORDER BY `Time` DESC LIMIT 1" % row['InstrumentsName']
    mydb.Execute(sql)

    nlastDate = mydb.FetchOne()

    if nlastDate == None:
        return instrument_details

    nlasttime = nlastDate['Time'] // 10**4
#===测试数据===
    if row['InstrumentsName'] == 'TF':
        nlasttime = 140612
    else:
        nlasttime = 140616
#===测试数据===
    nClosePrice = nlastDate['rClosePrice']
    # 增量场景 1：数据库最后一条记录日期大于Instrument_details配置开始时间。取最后一条期数+最后记录日期~当前系统时间
    #         2：最后一条记录日期小于Instrument_details配置开始时间 。结合上一条配置的期数补充
    ntmpExeclist = []
    tmpdict = {}

    cnt = len(instrument_details)

    for idx in range(cnt - 1, -1, -1):
        tmpdict["BeginTime"] = instrument_details[idx]['BeginTime']
        tmpdict["Period"] = instrument_details[idx]['Period']
        tmpdict["InstrumentsName"] = instrument_details[idx]['InstrumentsName']
        if nlasttime < int(instrument_details[idx]['BeginTime']):
            ntmpExeclist.append(tmpdict.copy())
        elif nlasttime == int(instrument_details[idx]['BeginTime']):
            tmpdict["isRev"] = 1
            tmpdict["nClosePrice"] = nClosePrice
            ntmpExeclist.append(tmpdict.copy())
            ntmpExeclist = sorted(
                ntmpExeclist, key=lambda _ntmpExeclist: _ntmpExeclist['Period'])
            return ntmpExeclist
        else:
            tmpdict["BeginTime"] = nlasttime
            ntmpExeclist.append(tmpdict.copy())
            ntmpExeclist = sorted(
                ntmpExeclist, key=lambda _ntmpExeclist: _ntmpExeclist['Period'])

            return ntmpExeclist


def get_Inscontinue_data(instrument_info, mydb):
    for row in instrument_info:
        sourcelist = []
        recoveredlist = []
        ntmpExeclist = []

        log.WriteLog('LOG_TRADE', "==incremental_update_begin instrument_info== %s" % (row['InstrumentsName']))
        resetlist = reset_Instrument_details(mydb, row)
        print("reset:", resetlist)
        log.WriteLog('LOG_TRADE', "reset: %s" % resetlist)
        for i, d in enumerate(resetlist):
            tlist = d
            tlist['Exchange'] = row['Exchange']
            if 'isRev' in d and 'nClosePrice' in d:
                recoveredlist = rec_closePrice(mydb, tlist, recoveredlist)
            if len(recoveredlist) > 0:
                recoveredlist = rec_closePrice(mydb, tlist, recoveredlist)
            if i < len(resetlist) - 1:
                endtime = resetlist[i + 1]['BeginTime']
            else:
                endtime = time.strftime('%y%m%d', time.localtime())
            tlist['Endtime'] = endtime
            reslist = get_hq_data(mydb, tlist)
            for v in reslist:
                sourcelist.append(v)
                recoveredlist.append(v.copy())

            if i == len(ntmpExeclist) - 1:
                lpara = {}
                lpara['InstrumentsName'] = row['InstrumentsName']

                con_gentodate(sourcelist, recoveredlist, lpara, mydb)


def continue_generate():
    mydb = func.create_database()
    # 查询合约-交易所信息表
    mydb.Execute("select InstrumentsName,Exchange from instrument_info")
    instrument_info = mydb.FetchAll()

    get_Inscontinue_data(instrument_info, mydb)
    log.WriteLog('LOG_TRADE', "finish")
continue_generate()
