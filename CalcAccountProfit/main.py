import os
import re
import sys
import string
import ConfigParser
import shutil
import db,log
import positions
import contract_info

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
		self.send_profit2db = ini_parser.get(session_name, "send_profit_to_database").lower() == "true"
		
def create_database(session_name):
	cfg = DB_Config("system.ini", session_name)
	database = db.DB(host=cfg.db_host,user=cfg.db_user, passwd=cfg.db_password, db=cfg.db_db, charset=cfg.db_charset, port=cfg.db_port)
	return database

def get_last_min(contract):
	contract_symbol = contract_info.get_contract_symbol(contract)
	if contract_symbol == 'IF' or contract_symbol == 'IH' or contract_symbol == 'IC':
		return 1515,1514,1500
	return 1500,1459

def query_close_price(database, contract, date):
	table_name = get_dbtable(contract)

	times = get_last_min(contract)
	rec = None
	for time in times:
		sql = "SELECT ClosePrice FROM %s WHERE time=%d%d && instrumentID='%s'" % (table_name, date%1000000, time, contract)
		database.Query(sql)
		rec = database.FetchOne()
		if rec:	break

	if not rec:
		log.WriteError('cant find %s close price %d [%s]' % (contract, date, sql))
		# err = 'cant find %s close price %d [%s]' % (contract, date, sql)
		# raise Exception, err
		rec = [0]
	close_price = rec[0]
	return close_price

def query_last_profit(db_profit, accountID, instrumentID):
	sql = "SELECT time, profit FROM fd_report_profit WHERE accountID='%s' && InstrumentID='%s' ORDER BY time DESC" % (accountID, instrumentID)
	db_profit.Query(sql)

	rec = db_profit.FetchOne()
	if not rec: return
	return rec

# 获取合约数据表的名字
def get_dbtable(contract):
	contract_symbol = contract_info.get_contract_symbol(contract)
	exg_config = contract_info.create_exg_config()
	exg = exg_config.get_contract_exchage(contract_symbol)

	return "hq_%s_k1" % (exg)

def read_records(trade_rec_file):
	file_name = trade_rec_file
	list_data = []
	index = 0
	if not os.path.exists(file_name):
		err = "file [%s] doesn't exist" %  file_name
		log.WriteError(err)
		raise Exception, err

	f = open(file_name, "rt")
	if not f: 
		err = 'cant open file [%s]' %  file_name
		log.WriteError(err)
		raise Exception
		return
		
	line = f.readline()
	while line:
		index += 1
		try:
			ma1 = re.search("(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
			ma2 = re.search("(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
			if ma1:
				arrs = ma1.groups()
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

				list_data.append([contract, date, hh*10000+mm*100+ss, trade_dir, trade_type, price, trade_num, commission, sysID])
			elif ma2:
				arrs = ma2.groups()
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
				sysID = arrs[10]

				list_data.append([contract, date, hh*10000+mm*100+ss, trade_dir, trade_type, price, trade_num, commission, sysID])
			else:
				log.WriteError("trade_records line %d not match!" % (index))
		except Exception, e:
			print e

		line = f.readline()
	f.close()
	return list_data

def parse_records(pos_manager, trading_days, records, db_data):
	infos = {
		"contracts" : {},
		"day_profit" : {},
		"day_pos_profit" : {},
		"day_margin" : {}
	}
	contracts = infos["contracts"]
	day_profits = infos["day_profit"]
	day_pos_profit = infos["day_pos_profit"]
	day_margins = infos["day_margin"]

	def func_query_close_price(contract, date):
		return query_close_price(db_data, contract, date)

	profit_file = {}
	close_profits = {}

	# 初始化当前日期
	current_calc_date = records[0][1]

	trading_day_idx = 0
	debug_days = []
	while True:
		if current_calc_date <= trading_days[trading_day_idx]: break
		trading_day_idx += 1
		if trading_day_idx >= len(trading_days): break

	def calc_day_position_profit(trading_day_idx, current_calc_date, date):
		while True: # 有交易日但没有交易记录，也要计算当天的净值
			if trading_days[trading_day_idx] < current_calc_date:
				trading_day_idx += 1
				if trading_day_idx >= len(trading_days): break
				
			td = trading_days[trading_day_idx]
			if td < date:
				print("trading_days[trading_day_idx]=", td, date)
				debug_days.append(td)
				day_profit, pos_profit = pos_manager.get_position_profit(td, func_query_close_price)
				day_margin = pos_manager.get_margin(td, func_query_close_price)
				day_profits[td] = day_profit
				day_pos_profit[td] = pos_profit
				day_margins[td] = day_margin
				current_calc_date = date
			else: break
		return current_calc_date, trading_day_idx

	for contract, date, hhmmss, trade_dir, trade_type, price, trade_num, commission, sys_id in records:
		symbol = get_contract_symbol(contract)

		if(not profit_file.has_key(symbol)):
			profit_file[symbol] = open("profit/%s_profit.db" % symbol, "w")

		if date > current_calc_date: #日期变化，计算日利润
			current_calc_date, trading_day_idx = calc_day_position_profit(trading_day_idx, current_calc_date, date)

		datetime = date* 1000000 + hhmmss
		dir = positions.DIR_BUY
		profit = 0

		if trade_dir == u'卖出': dir = positions.DIR_SELL
		if trade_type == u'开仓':
			pos_manager.open(datetime, contract, dir, trade_num, price, commission)
		else:
			profit = pos_manager.close(datetime, contract, dir, trade_num, price, commission, trade_type == u'平今')

		if not contracts.has_key(contract): contracts[contract] = 0
		if(close_profits.has_key(symbol)):
			close_profits[symbol] += profit
		else:
			close_profits[symbol] = profit

		profit_file[symbol].write("%d\t%d\t%.2f\t%.2f\t%.2f\t%.2f\t%d\n" % (date%1000000*10000+hhmmss/100, dir, price, profit, close_profits[symbol], commission, trade_num))
	
	calc_day_position_profit(trading_day_idx, current_calc_date, trading_days[-1]+1)

	for k,v in contracts.items():
		contracts[k] = (pos_manager.get_profit(k), pos_manager.get_commission(k), 
			pos_manager.get_pos_profit(k, trading_days[-1], func_query_close_price),
			pos_manager.get_pos_price(k,positions.DIR_BUY), pos_manager.get_pos_price(k,positions.DIR_SELL))

	# 关闭所有文件
	[v.close() for k,v in profit_file.items()]
	return infos

def get_trading_day(db_profit, begin_day):
	sql = "select time from fd_report_profit where time >=%s group by time order by time" % begin_day
	db_profit.Query(sql)
	recs = db_profit.FetchAll()
	if not recs:	
		err = 'query trading day failed, begin day [%d]' %  begin_day
		raise Exception, err
		return
	return [rec[0] for rec in recs]

def calc_day_profit(sys_config, db_profit, trading_days, contracts, day_contract_profits, day_margins):
	contracts.sort()

	# 保存打印
	title = "日期"
	for c in contracts:
		title += "\t" + c

	log.WriteLog("net_profit", title)

	for day in trading_days:
		line = "%s" % day
		for c in contracts:
			if day_contract_profits.has_key(day) and day_contract_profits[day].has_key(c):
				line += "\t%.2f" % day_contract_profits[day][c]
			else:
				line += "\t0"
		log.WriteLog("net_profit", line)

	# 合并合约
	day_symbol_profits = {}
	for day in trading_days:
		if not day_symbol_profits.has_key(day): day_symbol_profits[day] = {}
		for c in contracts:
			if day_contract_profits.has_key(day) and day_contract_profits[day].has_key(c):
				symbol = contract_info.get_contract_symbol(c)
				if not day_symbol_profits[day].has_key(symbol): day_symbol_profits[day][symbol] = 0
				day_symbol_profits[day][symbol] += day_contract_profits[day][c]

	profit_sqls = []
	margin_sqls = []
	for day in trading_days:
		for symbol, profit in day_symbol_profits[day].items():
			sql = "REPLACE INTO fd_report_profit(accountID,time,instrumentID,profit) VALUES('%s', %s, '%s', %d);" % (sys_config.fund_account, day, symbol, profit)
			profit_sqls.append(sql)

		if day_margins.has_key(day):
			sql = "REPLACE INTO fd_report_margin(accountID,time,margin) VALUES('%s', %s, %d);" % (sys_config.fund_account, day, day_margins[day])
			margin_sqls.append(sql)

	for sql in profit_sqls:
		log.WriteLog("net_profit_sql", sql)

	for sql in margin_sqls:
		log.WriteLog("net_margin_sql", sql)

	if sys_config.send_profit2db:
		for sql in sqls:
			db_profit.Execute(sql)
		db_profit.Commit()

def make_log_dir():
	base_path = os.getcwd()
	log_path = os.path.join(base_path, "log")
	if not os.path.exists(log_path):
		os.makedirs(log_path)
	else:
		shutil.rmtree(log_path)
		os.makedirs(log_path)

def make_profit_dir():
	base_path = os.getcwd()
	profit_path = os.path.join(base_path, "profit")
	if not os.path.exists(profit_path):
		os.makedirs(profit_path)
	else:
		shutil.rmtree(profit_path)
		os.makedirs(profit_path)

def get_contract_symbol(contract):
	m = re.match("(\D+)\d*", contract)
	return m.groups()[0]

def main():
	make_log_dir()
	make_profit_dir()

	trade_rec_file = "trade_records.db"
	if len(sys.argv) > 1:
		trade_rec_file = sys.argv[1]

	db_data = create_database("db_data")
	db_profit = create_database("db_profit")

	exg_config = contract_info.create_exg_config()
	pos_manager = positions.PositionsManager()
	sys_config = Sys_config("system.ini", "fund_info")

	# 加载合约信息（乘数）
	contract_info.load_contract_mul()
	# 加载合约信息（保证金率）
	contract_info.load_contract_mar()

	# 获取该品种最后记录的净值
	# rec = query_last_profit(db_profit, "virtual_tm_3", "mesh_ru")

	# 读取交易记录
	records = read_records(trade_rec_file)
	if len(records) == 0:
		raise Exception, 'cant read trading record!'
		return

	# 获取起始交易日,查询所有交易日
	trading_day = records[0][1]
	trading_days = get_trading_day(db_profit, trading_day)

	# 分析交易收益
	infos = parse_records(pos_manager, trading_days, records, db_data)

    # 计算每日净值
	calc_day_profit(sys_config, db_profit, trading_days, infos["contracts"].keys(), infos["day_profit"], infos["day_margin"])

	log.WriteLog("result", "----------------")
	log.WriteLog("result", "result:\t合约\t平仓收益\t手续费")
	for c,v in infos["contracts"].items():
		log.WriteLog("result", "result:\t%s\t%.2f\t%.2f"%(c, v[0], v[1]))

	log.WriteLog("result", "----------------")
	log.WriteLog("result", "position profit")

	K = infos["day_pos_profit"].keys()
	K.sort()

	total = 0
	for c, v in infos["day_pos_profit"][K[-1]].items():
		log.WriteLog("result", "%s:\t%s" %(c, v))
		total +=v
	log.WriteLog("result", "total:\t%s" % total)

	pos_manager.print_position()


if __name__ == '__main__':
	try:
		main()
	except Exception, e:
		log.WriteError(e[0])
		import traceback
		print traceback.print_exc()

