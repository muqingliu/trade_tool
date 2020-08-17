import re
import sys
import string
import ConfigParser
import db,log

class DB_Config(object):
	# 配置文件信息结构
	def __init__(self, path_ini, session_name):
		ini_parser = ConfigParser.ConfigParser()
		ini_parser.read(path_ini)

		self.db_host = ini_parser.get(session_name, "host")
		self.db_user = ini_parser.get(session_name, "user")
		self.db_password = ini_parser.get(session_name, "password")
		self.db_db = ini_parser.get(session_name, "db")
		self.db_port = string.atoi(ini_parser.get(session_name, "port"))
		self.db_charset = ini_parser.get(session_name, "charset")

class Sys_config(object):
	def __init__(self, path_ini, session_name):
		ini_parser = ConfigParser.ConfigParser()
		ini_parser.read(path_ini)

		self.fund_account = ini_parser.get(session_name, "fund_account")
		
def create_database(session_name):
	cfg = DB_Config("system.ini", session_name)
	database = db.DB(host=cfg.db_host,user=cfg.db_user, passwd=cfg.db_password, db=cfg.db_db, charset=cfg.db_charset, port=cfg.db_port)
	return database

def read_records(trade_rec_file):
	file_name = trade_rec_file
	list_data = []
	index = 1
	f = open(file_name, "rt")
	if not f: 
		err = 'cant open file [%s]' %  file_name
		raise Exception, err
		return
		
	line = f.readline()
	while line:
		try:
			ma = re.search("(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
			if ma:
				arrs = ma.groups()
				date = int(arrs[0])
				hh = int(arrs[1])
				mm = int(arrs[2])
				ss = int(arrs[3])
				contract = arrs[4]
				trade_dir = arrs[5].decode('gbk')
				trade_type = arrs[6].decode('gbk')
				price = float(arrs[7])
				trade_num = int(arrs[8])
				commission = float(arrs[9])
				touji = arrs[10]
				sysID = arrs[11]

				list_data.append([contract, date%1000000, hh*10000+mm*100+ss, trade_dir, trade_type, price, trade_num, commission, sysID])
			else:
				print "line %d not match!" % (index)

		except Exception, e:
			print e

		line = f.readline()
	f.close()
	return list_data

def send_record2db(sys_config, db_profit, records):
	for rec in records:
		contract = rec[0] 
		date = rec[1] 
		time = rec[2] 
		trade_dir = rec[3] 
		trade_type = rec[4] 
		price = rec[5] 
		trade_num = rec[6] 
		commission = rec[7]
		sys_id = rec[8]

		sql = "REPLACE INTO fd_report_trade_record(tradeName, contract, sysID, type, tradeDate, tradeTime, dir, price, commission, number) VALUES('%s', '%s', %s, '%s', %d, %d, '%s', %.2f, %.2f, %d);"  \
		% (sys_config.fund_account, contract, sys_id, trade_type, date, time, trade_dir, price, commission, trade_num)
		
		log.WriteLog("record_sql", sql)

		db_profit.Execute(sql.encode('utf8'))

	db_profit.Commit()


def main():
	trade_rec_file = "trade_records.db"
	if len(sys.argv) > 1:
		trade_rec_file = sys.argv[1]

	db_profit = create_database("db_profit")

	sys_config = Sys_config("system.ini", "fund_info")

	# 读取交易记录
	records = read_records(trade_rec_file)
	if len(records) == 0:
		raise Exception, 'cant read trading record!'
		return
	
	send_record2db(sys_config, db_profit, records)


if __name__ == '__main__':
	try:
		main()
	except Exception, e:
		log.WriteError(e[0])
		import traceback
		print traceback.print_exc()

