#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from tools import db

# @profile
def main():
    dirname = "hq_shfe_k1"
    #dirname = "hq_dce_k1"
    # dirname = "hq_cffex_k1"
    # dirname = "hq_czce_k1"
    # contract = "SR"
    root_dir = os.getcwd()
    fullpath = "%s\\%s" % (root_dir, dirname)
    if not os.path.exists(fullpath):
        os.mkdir(fullpath)

    # db_host = "183.131.76.91"
    # db_user = "root"
    # db_pwd  = "P)O(I*U&Y^"
    # db_dbase= "stock"
    # db_port = 3308
    db_host = "www.5656k.com"
    db_user = "stock"
    db_pwd  = "P)O(I*U&Y^"
    db_dbase= "stock_realtime"
    db_port = 3308

    database = db.DB(host=db_host,user=db_user, passwd=db_pwd, db=db_dbase, table_name='', port=db_port)

    # sqlStatement = "SELECT DISTINCT InstrumentID AS FileName FROM %s WHERE `InstrumentID` LIKE '%%%s%%'" % (dirname, contract)
    # print sqlStatement
    # database.Execute(sqlStatement)
    # name_info_list = database.FetchAll()

    # contracts = [c[0] for c in name_info_list]
    # contracts = ["ru1509"]
    contracts = ["rb1805"]

    for name in contracts:
        out = open("%s\\%s.txt" % (fullpath, name), "wb")

        sqlStatement = "SELECT Time,OpenPrice,HighestPrice,LowestPrice,ClosePrice,Volume FROM %s WHERE `InstrumentID` = '%s' AND \
                       `Time` > 1705311600 AND `Time` < 1803201600 ORDER BY `Time`" % (dirname, name)
        database.Execute(sqlStatement)

        contract_info_list = database.FetchAll()
        for contract_info in contract_info_list:
            time = int(contract_info[0])
            time_str = "%u/%02u/%02u-%02u:%02u" % (2000 + int(time / 100000000), int(time / 1000000) % 100, int(time / 10000) % 100, 
                       int(time / 100) % 100, time % 100)
            open_price = float(contract_info[1])
            high_price = float(contract_info[2])
            low_price = float(contract_info[3])
            close_price = float(contract_info[4])
            volume = float(contract_info[5])

            content = "%s\t%.04f\t%.04f\t%.04f\t%.04f\t%.04f\r\n" % (time_str, open_price, high_price, low_price, close_price, volume)

            out.write(content)

        out.close()

if __name__ == '__main__':
    
    main()
