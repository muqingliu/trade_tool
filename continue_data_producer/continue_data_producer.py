import db
import log
import os
import re
import sys
import exchange_config
import string
import subprocess
import ConfigParser

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

class MainContractCfg(object):
	def __init__(self, path_ini):
		self.ini_parser = ConfigParser.ConfigParser()
		self.ini_parser.read(path_ini)
		self.path_ini = path_ini

		self.old_main_contracts = {}
		for pair in self.ini_parser.items("main_contract"):
			self.old_main_contracts[pair[0]] = pair[1]

	def UpdateMainContract(self, symbol, contract):
		self.old_main_contracts[symbol] = contract
		self.ini_parser.set("main_contract", symbol, contract)
		self.ini_parser.write(open(self.path_ini, "w"))

class SystemInfo(object):
	"""docstring for SystemInfo"""
	def __init__(self, path_ini):
		ini_parser = ConfigParser.ConfigParser()
		ini_parser.read(path_ini)

		self.continue_data_path = ini_parser.get("data_path", "continue_data")
		self.gaps_path = ini_parser.get("data_path", "gaps_data")
		self.last_exe = ini_parser.get("execute", "last_exe")

def get_symbol(contract):
	ma = re.search("([A-Za-z]+)(\d+)", contract)
	if ma:
		arrs = ma.groups()
		symbol = arrs[0]
		return symbol
	return ""

def get_number(contract):
	ma = re.search("([A-Za-z]+)(\d+)", contract)
	if ma:
		arrs = ma.groups()
		symbol = arrs[1]
		return symbol
	return ""

def create_database(session_name):
	cur_path = os.path.split(sys.argv[0])[0]
	sys_full_path = os.path.join(cur_path, "system.ini")
	cfg = DB_Config(sys_full_path, session_name)
	database = db.DB(host=cfg.db_host,user=cfg.db_user, passwd=cfg.db_password, db=cfg.db_db, charset=cfg.db_charset, port=cfg.db_port)
	return database

def judge_main_contract(rec_first, rec_second):
	if rec_first[2] >= rec_second[2] and rec_first[3] >= rec_second[3]:
		return rec_first[1]
	elif rec_first[2] <= rec_second[2] and rec_first[3] <= rec_second[3]:
		return rec_second[1]
	else:
		number_first = get_number(rec_first[1])
		number_second = get_number(rec_second[1])
		if number_first < number_second:
			return rec_first[1]
		else:
			return rec_second[1]

	return ""

def get_main_contract(db, symbol, trading_day):
	if not db.IsConnect():
		return ("","")

	sql = "select date,contract,open_interest,volume from contract_info where contract LIKE '%s____' and date<=%u order by date " \
			"DESC,open_interest DESC" % (symbol, trading_day % 1000000)
	db.Query(sql)
	recs = db.FetchAll()
	if not recs:
		err = 'get main contract of [%s] records failed, trading day[%d]' % (symbol, trading_day)
		return ("","")

	cur_rec_first = None
	cur_rec_second = None
	pre_rec_first = None
	pre_rec_second = None
	cur_trading_day = 0
	for index,rec in enumerate(recs):
		if cur_trading_day == 0:
			cur_trading_day = int(rec[0])
			cur_rec_first = rec
			cur_rec_second = recs[index+1]
		elif int(rec[0]) != cur_trading_day:
			cur_trading_day = int(rec[0])
			pre_rec_first = rec
			pre_rec_second = recs[index+1]
			break

	cur_main_contract = judge_main_contract(cur_rec_first, cur_rec_second)
	pre_main_contract = judge_main_contract(pre_rec_first, pre_rec_second)
	if cur_main_contract == pre_main_contract:
		return (cur_main_contract,pre_main_contract)
	else:
		return (pre_main_contract,cur_main_contract)

	return ("","")

def get_symbol_latest_min(filepath):
	with open(filepath, "rb") as fp:
		klines = fp.readlines()
		length = len(klines)
		if length > 0:
			kline_str = klines[length - 1]
			kline_info_list = kline_str.split('\t')
			time_str = kline_info_list[0]
			ma = re.search("(\d{4})/(\d{2})/(\d{2})-(\d{2}):(\d{2})", time_str)
			if ma:
				arrs = ma.groups()
				latest_min = string.atoi("%s%s%s%s%s" % (arrs[0][2:],arrs[1],arrs[2],arrs[3],arrs[4]))
				return latest_min

	return 0

def get_klines(db, exg_cfg, contract, latest_min):
	symbol = get_symbol(contract)
	exchange = exg_cfg.get_contract_exchage(symbol)
	table = "hq_%s_k1" % exchange
	sql = "select * from %s where InstrumentID='%s' and Time>%u" % (table, contract, latest_min)
	print sql
	db.Query(sql)
	recs = db.FetchAll()
	klines = []
	if recs and len(recs) > 0:
		for rec in recs:
			kline = [rec[1],int(rec[2]),float(rec[3]),float(rec[4]),float(rec[5]),float(rec[6]),int(rec[7])]
			klines.append(kline)
			
	return klines

def get_trading_day(klines, size, begin_index):
	for i in xrange(begin_index,size):
		kline = klines[i]
		time = kline[1]
		if time % 10000 >= 800 and time % 10000 < 1600:
			return time / 10000

	return 0

def update_gaps(rootdir, symbol, cur_min):
	filename = "%s\\%sgaps.txt" % (rootdir, symbol)
	with open(filename, "a+") as fp:
		gaps_list = fp.readlines()
		size = len(gaps_list)
		if size > 0:
			exist = False
			for i in xrange(0,size):
				gap = gaps_list[size - 1 - i]
				ma = re.match("(\d{4})/(\d{2})/(\d{2})", gap)
				if ma:
					arrs = ma.groups()
					last_day = int(arrs[0]) % 100 * 10000 + int(arrs[1]) * 100 + int(arrs[2])
					if last_day == cur_min / 10000:
						exist = True
						break

			if not exist:			
				fp.write("20%02u/%02u/%02u-%02u:%02u\n" % (cur_min / 100000000,
					cur_min / 1000000 % 100, cur_min / 10000 % 100, 
					cur_min / 100 % 100, cur_min % 100))
		else:
			fp.write("20%02u/%02u/%02u-%02u:%02u\n" % (cur_min / 100000000,
				cur_min / 1000000 % 100, cur_min / 10000 % 100, 
				cur_min / 100 % 100, cur_min % 100))

def main():
	cur_path = os.path.split(sys.argv[0])[0]
	db_price = create_database("db_data")
	main_contract_cfg = MainContractCfg(os.path.join(cur_path, "main_contract.ini"))
	sys_info = SystemInfo(os.path.join(cur_path, "system.ini"))
	exg_cfg = exchange_config.exchange_config(os.path.join(cur_path, "exchange.ini"))
	for parentdir,dirnames,filenames in os.walk(sys_info.continue_data_path,False):
		for filename in filenames:
			index = filename.find("L0.txt")
			if -1 == index:
				continue

			filepath = os.path.join(parentdir, filename)
			latest_min = get_symbol_latest_min(filepath)
			latest_day = latest_min / 10000 + 20000000

			symbol = filename[:index]
			print filename, symbol
			main_contract_set = get_main_contract(db_price, symbol, latest_day)
			main_contract = main_contract_set[0]
			while True:
				klines = get_klines(db_price, exg_cfg, main_contract, latest_min)
				print latest_min,main_contract
				
				size = len(klines)
				last_index = -1
				not_end = False
				last_trading_day = latest_day
				trading_day = latest_day
				#需考虑股指，当还是主力合约的时候，便已经没有后续行情了的情况，将次主力合约设为主力合约，并更新文件
				if size == 0:
					main_contract = main_contract_set[1]
					print latest_min,main_contract

					klines = get_klines(db_price, exg_cfg, main_contract, latest_min)
					size = len(klines)
					if 0 == size:
						break

					update_gaps(sys_info.gaps_path, symbol, klines[0][1])
					main_contract_cfg.UpdateMainContract(symbol, main_contract)

				for i in xrange(0,size):
					kline = klines[i]

					main_contract_temp = main_contract
					if i == 0:
						trading_day = get_trading_day(klines, size, i)
						main_contract_temp_set = get_main_contract(db_price, symbol, trading_day)
						main_contract_temp = main_contract_temp_set[0]
					else:
						last_kline = klines[last_index]
						if last_kline[1] % 10000 <= 1600 and (kline[1] % 10000 >= 2000 or last_kline[1] / 10000 != kline[1] / 10000 
							and kline[1] % 10000 >= 800):
							last_trading_day = trading_day
							trading_day = get_trading_day(klines, size, i)
							main_contract_temp_set = get_main_contract(db_price, symbol, trading_day)
							main_contract_temp = main_contract_temp_set[0]

					number_main_temp = get_number(main_contract_temp)
					number_main = get_number(main_contract)
					if main_contract_temp != main_contract and number_main_temp > number_main:
						print trading_day,main_contract_temp
						main_contract = main_contract_temp
						update_gaps(sys_info.gaps_path, symbol, kline[1])
						main_contract_cfg.UpdateMainContract(symbol, main_contract)
						not_end = True
						if last_index >= 0:
							latest_min = klines[last_index][1]
						latest_day = last_trading_day
						break

					with open(filepath, "a+") as fp:
						content = "20%u/%02u/%02u-%02u:%02u\t%.4f\t%.4f\t%.4f\t%.4f\t%u\n" % (kline[1]/100000000, 
							kline[1]/1000000%100, kline[1]/10000%100, kline[1]/100%100, kline[1]%100,
							kline[2], kline[4], kline[5], kline[3], kline[6])
						fp.write(content)

					last_index = i

				if not not_end:
					break

	if len(sys_info.last_exe) > 0 and os.path.exists(sys_info.last_exe) and os.path.isfile(sys_info.last_exe) \
		and os.path.splitext(sys_info.last_exe)[1] == '.exe':
		print sys_info.last_exe
		subprocess.Popen(sys_info.last_exe)

if __name__ == '__main__':
	main()