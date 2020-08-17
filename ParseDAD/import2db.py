#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
from tools import db
from exchange_config import *

def read_origin_data(file_name, num):
	list_data = []
	index = num
	f = open(file_name, "rt")
	if f:
		l = f.readline()
		while l:
			try:
				ma = re.findall("(\d+)/(\d+)/(\d+)-(\d+):(\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)$", l)
				if ma:
					y = ma[0][0]
					m = ma[0][1]
					d = ma[0][2]
					h = ma[0][3]
					mm= ma[0][4]
					_open = ma[0][5]
					_hith = ma[0][6]
					_low  = ma[0][7]
					_close= ma[0][8]
					_num  = ma[0][9]
					list_data.append([y,m,d,h,mm,_open,_hith,_low,_close,_num])
				else:
					print("line %d not match!" % (num -index))

			except Exception as e:
				print(e)
			l = f.readline()
			index -=1
			if index <=0: break
		f.close()

	return list_data

def process(contract, period):
	# read_file_name = "auL0.txt"
	# contract_period = 1605

	read_number = 999999999999
	read_exg_ini = "exchange.ini"

	db_host = "127.0.0.1"
	db_user = "root"
	db_pwd  = "1"
	db_dbase= "stock"

	datas = read_origin_data("input/d_%sL0.txt" % contract, read_number)

	# database = db.DB(host=db_host,user=db_user, passwd=db_pwd, db=db_dbase)
	# contract_mc = re.match("(\w{,2})L0.*", read_file_name)
	# if not contract_mc:
	# 	print("源文件名字非法 ")
	# 	return

	# contract = contract_mc.group(1)
	exg_cfg = exchange_config(read_exg_ini)
	exg_name = exg_cfg.get_contract_exchage(contract)
	db_table_name = "hq_%s_k1" % exg_name.lower()
	instrument = "%s%d" % (contract, period)

	sql0 = "delete from %s where InstrumentID = '%s';" % (db_table_name, instrument)
	
	sqls = []
	begin_idx = 0
	max_num = 4000
	size = len(datas)
	while begin_idx < size:
		end_idx = min(size, begin_idx + max_num)

		sql = "INSERT INTO %s(`InstrumentID`, `Time`,`OpenPrice`,`HighestPrice`,`LowestPrice`, `ClosePrice`,`Volume`) VALUES\n" % (db_table_name)

		for i in xrange(begin_idx,end_idx):
			data = datas[i]

			time = "%d%s%s%s%s" % (int(data[0])%100, data[1], data[2], data[3], data[4])
			if i == end_idx - 1:
				sql += "('%s', %s, %f, %f, %f, %f, %s);\n" % \
			  	  	   (instrument, time, float(data[5]), float(data[6]), float(data[7]), float(data[8]), data[9])
			
			else:
				sql += "('%s', %s, %f, %f, %f, %f, %s),\n" % \
			  		  (instrument, time, float(data[5]), float(data[6]), float(data[7]), float(data[8]), data[9])

		sqls.append(sql)

		begin_idx = begin_idx + max_num

	out = open("output/%s%d.sql" % (contract, period), "w")
	out.write(sql0 + "\n")
	for sql in sqls:
		out.write(sql+"\n")
	out.close()


if __name__ == '__main__':
	
	contracts =(
	("ru", 1609), 
	("rb", 1610), 
	("cu", 1605), 
	("au", 1606), 
	("FG", 1605), 
	("j", 1605), 
	("jm", 1605), 
	("l", 1605), 
	("SR", 1609), 
	("TA", 1605), 
	)

	for c,p in contracts:
		process(c,p)

