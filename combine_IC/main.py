import db

change_period_dates = [150515, 150619, 150717, 150821, 150918, 151016, 151120, 151218, 160115, 160219, 160318, 160415, 160520, 160617, 160715, 
                        160819, 160919, 161021, 161118, 161216, 170120, 170217, 170317, 170421, 170519]

def get_instrumentID(database):
    database.Query("select distinct instrumentID from hq_cffex_k1")
    recs = database.FetchAll()
    ids = [rec[0] for rec in recs]
    return ids


def get_instrument_days(database, ids):
    days = {}
    for id in ids:
        database.Query("select distinct floor(time /10000) from hq_cffex_k1 where instrumentID = '%s'" % id)

        recs = database.FetchAll()
        days[id] = [rec[0] for rec in recs]

    return days


def combine_datas(database, ids, days):
    switch_day = 0
    last_period_price = 0
    offset = 0
    datas = []
    idx = 0
    for id in ids:
        time_begin = switch_day
        if time_begin == 0:
            time_begin = days[id][0] * 10000 + 1500

        time_end = days[id][-7] * 10000 + 1500
        switch_day = time_end
        print id, time_begin, time_end, len(days[id])
        sql = "select time, openPrice, HighestPrice, LowestPrice, closePrice, Volume from hq_cffex_k1 where instrumentID = '%s' && time>= %s && time <= %s" %(id, time_begin, time_end)
        database.Query(sql)

        recs = database.FetchAll()
        # print recs[-1][4]
        if last_period_price != 0:
            offset += recs[0][4] - last_period_price
            print "subdata", recs[0][4] , last_period_price, recs[0]
        datas.extend([[rec[0], rec[1] - offset, rec[2] - offset, rec[3] - offset, rec[4] - offset, rec[5]] for rec in recs[1:]])
        last_period_price = recs[-1][4]
        print "offset:",offset
        idx+=1

    return datas


def combine_datas(database, change_period_dates):
    last_period_price = 0
    last_change_period_date = 0
    offset = 0
    datas = []
    for change_period_date in change_period_dates:
        # id = "IC%u" % (change_period_date / 100)
        id = "IC%u" % (change_period_date / 100 + 1)
        if change_period_date / 100 % 100 == 12:
            id = "IC%u" % ((change_period_date / 10000 + 1) * 100 + 1)

        print change_period_date,id

        time_begin = last_change_period_date * 10000 + 900
        if last_change_period_date == 0:
            time_begin = 0
        time_end = change_period_date * 10000 + 900

        sql = "select time,openPrice,HighestPrice,LowestPrice,closePrice,Volume from hq_cffex_k1 where instrumentID='%s' && time>=%s && time<%s" % (id, time_begin, time_end)
        print sql
        database.Query(sql)

        recs = database.FetchAll()

        # if last_period_price != 0:
        #     offset += recs[0][1] - last_period_price
        #     print offset

        for rec in recs:
            datas.extend([[rec[0], rec[1], rec[2], rec[3], rec[4], rec[5]]])
            last_period_price = rec[4]

        last_change_period_date = change_period_date

    return datas


def main():
    database = db.DB("127.0.0.1", "root", "1", "stock_virtual", port = 3306)

    datas = combine_datas(database, change_period_dates)

    f = open("ICL0.txt", "w+")
    if f:
        for line in datas:
            datetime = int(line[0])
            yyyy = datetime / 100000000
            mm = datetime / 1000000 % 100
            dd = datetime / 10000 % 100
            hh = datetime / 100 % 100
            MM = datetime % 100
            dt_format = "20%s/%02d/%02d-%02d:%02d" % (yyyy, mm, dd, hh, MM)
            f.write("%s\t%.1f\t%.1f\t%.1f\t%.1f\t%d\n" %(dt_format,line[1],line[2],line[3],line[4],line[5]))
        f.close()

    # ids = get_instrumentID(database)
    # days = get_instrument_days(database, ids)

    # datas = combine_datas(database, ids, days)

    # f = open("ICL0", "w+")
    # if f:
    #     for line in datas:
    #         datetime = int(line[0])
    #         yyyy = datetime / 100000000
    #         mm = datetime / 1000000 % 100
    #         dd = datetime / 10000 % 100
    #         hh = datetime / 100 % 100
    #         MM = datetime % 100
    #         dt_format = "20%s/%02d/%02d-%02d:%02d" % (yyyy, mm, dd, hh, MM)
    #         f.write("%s\t%.1f\t%.1f\t%.1f\t%.1f\t%d\n" %(dt_format,line[1],line[2],line[3],line[4],line[5]))
    #     f.close()




if __name__ == '__main__':
    main()

