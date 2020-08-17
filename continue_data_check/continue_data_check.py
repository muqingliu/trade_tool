# -*- coding: utf-8 -*-

import ConfigParser
import exchange_config
import db
import string

class SystemInfo(object):
	"""docstring for SystemInfo"""
	def __init__(self, path_ini):
		ini_parser = ConfigParser.ConfigParser()
		ini_parser.read(path_ini)

		self.period_data_path = ini_parser.get("data_path", "period_data")

		self.db_host = ini_parser.get("db_data", "host")
		self.db_user = ini_parser.get("db_data", "user")
		self.db_password = ini_parser.get("db_data", "password")
		self.db_db = ini_parser.get("db_data", "db")
		self.db_port = string.atoi(ini_parser.get("db_data", "port"))

def get_data_by_period(db, exg_cfg, symbol, period):
	exchange_name = exg_cfg.get_contract_exchage(symbol)
	table = "hq_%s_k1" % exchange_name
	sql = "select * from %s where `InstrumentID` like '%s__%s'" % (table, symbol, period)
	recs = db.Query(sql)
	for rec in recs:
		contract = rec[1]
		time = rec[2]
		open = rec[3]
		close = rec[4]
		high = rec[5]
		low = rec[6]
		volume = rec[7]

def main():
	sys_info = SystemInfo("system.ini")
	exg_cfg = exchange_config.exchange_config("exchange.ini")
	db_data = db.DB(sys_info.db_host, sys_info.db_user, sys_info.db_password, sys_info.db_db, port = sys_info.db_port)
	get_data_by_period(db_data, exg_cfg, "rb", "01")

if __name__ == '__main__':
	main()