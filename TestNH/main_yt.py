import re,os,sys
import log
import positions

TRADE_LQ = False

def read_records(trade_rec_file):
	file_name = trade_rec_file
	map_data = []
	index = 1
	f = open(file_name, "rt")
	if not f: 
		err = 'cant open file [%s]' %  file_name
		raise Exception(err)
		return
		
	line = f.readline()
	while line:
		index += 1
		try:
			ma = re.match("(\d+)\s+(\d+)\s+(\w+)\s+(\S+)\s+(\d+.\d+)\s+(\d+)\s+(\d+.\d+)\s+(\d+)\s+(\d+)-(\d+)-(\d+)_(\d+):(\d+):(\d+)$", line)
			if ma:
				arrs = ma.groups(0)
				tradeID = arrs[0]
				accountID = arrs[1]
				contract = arrs[2]
				trade_dir = arrs[3].decode('utf8')
				price = float(arrs[4])
				trade_num = int(arrs[5])
				commission = float(arrs[6])
				orderID = int(arrs[7])
				year = int(arrs[8])
				month = int(arrs[9])
				day = int(arrs[10])
				hh = int(arrs[11])
				mm = int(arrs[12])
				ss = int(arrs[13])

				map_data.append([tradeID, accountID, contract, trade_dir, price, trade_num, commission, orderID, year*10000+month*100+day, hh*10000+mm*100+ss])
			else:
				print("line %d not match!" % (index))

		except Exception as e:
			print(e)

		line = f.readline()
	f.close()

	return map_data

def get_price(datas, datetime):
	if datetime in datas[0]:
		return datas[0][datetime][8]
	else:
		return 0

def get_pre_price(datas, datetime):
	for i in range(0, len(datas[1])):
		if datetime in datas[1][0]:
			return i - 1
	return 0

def get_next_price(datas, datetime):
	for i in range(0, len(datas[1])):
		if datetime in datas[1][0]:
			return i + 1
	return 0

def parse_records(pos_manager, records):
	infos = {
		"contracts" : {},
		"day_profit" : {},
		"day_accountID" : {},
		"day_contracts" : {},
		"day_times" : {}
	}
	contracts = infos["contracts"]
	all_profits = infos["day_profit"]
	day_accountID = infos["day_accountID"]
	day_contracts = infos["day_contracts"]
	day_times = infos["day_times"]

	def func_query_close_price(contract, date):
		return 1

	profit_file = {}
	close_profits = {}

	# 初始化当前日期
	set_accountID = []
	set_contracts = []
	trade_times = 0
	current_date = records[0][8]
	index = 1
	for tradeID, accountID, contract, dir, price, trade_num, commission, orderID, date, hhmmss in records:
		index += 1
		datetime = date * 1000000 + hhmmss

		if(not profit_file.has_key(contract)):
			profit_file[contract] = open("profit/%s_profit.db" % contract, "w")

		if current_date != date: #日期变化，计算日利润
			day_profit = pos_manager.get_position_profit(int(datetime/100), func_query_close_price)
			all_profits[current_date] = day_profit

			day_accountID[current_date] = set_accountID
			set_accountID = []

			day_contracts[current_date] = set_contracts
			set_contracts = []

			day_times[current_date] = trade_times
			trade_times = 0

			current_date = date

		trade_times = trade_times + 1

		if contract not in set_contracts:
			set_contracts.append(contract)

		if accountID not in set_accountID:
			set_accountID.append(accountID)

		profit = 0
		trade_dir = positions.DIR_BUY
		dir_reverse = positions.DIR_SELL
		if dir == u'买入':
			trade_dir = positions.DIR_SELL
			dir_reverse = positions.DIR_BUY

		num_reverse = pos_manager.get_num(contract, dir_reverse)
		if num_reverse < trade_num:
			pos_manager.open(datetime, contract, trade_dir, trade_num, price, commission)
		else:
			profit = pos_manager.close(datetime, contract, trade_dir, trade_num, price, commission, False)

		if not contracts.has_key(contract): contracts[contract] = 0
		if(close_profits.has_key(contract)):
			close_profits[contract] += profit
		else:
			close_profits[contract] = profit

		profit_file[contract].write("%d\t%d\t%.2f\t%.2f\t%.2f\t%.2f\t%d\n" % (date%1000000*10000+hhmmss/100, trade_dir, price, profit, close_profits[contract], commission, trade_num))

	# 记录最后一天日利润
	day_profit = pos_manager.get_position_profit(int(datetime/100), func_query_close_price)
	all_profits[current_date] = day_profit

	day_accountID[current_date] = set_accountID
	day_contracts[current_date] = set_contracts
	day_times[current_date] = trade_times

	for k,v in contracts.items():
		contracts[k] = (pos_manager.get_profit(k), pos_manager.get_commission(k))

	# 关闭所有文件
	[v.close() for k,v in profit_file.items()]

	return infos

def make_profit_dir():
	base_path = os.getcwd()
	if not os.path.exists(base_path + "/profit"): os.makedirs(base_path+"/profit") 

def calc_day_profit(contracts, day_contract_profits, day_contracts, day_accountID, day_times):
	contracts.sort()

	# 保存打印
	title = "日期"
	for c in contracts:
		title += "\t" + c

	log.WriteLog("net_profit", title)

	days = day_contract_profits.keys()
	days.sort()
	for day in days:
		line = "%s" % day
		for c in contracts:
			if day_contract_profits[day].has_key(c):
				line += "\t%.2f" % day_contract_profits[day][c]
			else:
				line += "\t0"
		log.WriteLog("net_profit", line)

	title = "日期\t合约"

	log.WriteLog("day_contracts", title)

	days = day_contracts.keys()
	days.sort()
	for day in days:
		line = "%s" % day
		set_contracts = day_contracts[day]
		size = len(set_contracts)
		for i in xrange(0,size):
			if 0 == i:
				line += "\t%s" % set_contracts[i]
			else:
				line += ",%s" % set_contracts[i]
		log.WriteLog("day_contracts", line)

	title = "日期\t账号ID"

	log.WriteLog("day_accountID", title)

	days = day_accountID.keys()
	days.sort()
	for day in days:
		line = "%s" % day
		set_accountID = day_accountID[day]
		size = len(set_accountID)
		for i in xrange(0,size):
			if 0 == i:
				line += "\t%s" % set_accountID[i]
			else:
				line += ",%s" % set_accountID[i]
		log.WriteLog("day_accountID", line)

	title = "日期\t交易次数"

	log.WriteLog("day_times", title)

	days = day_times.keys()
	days.sort()
	for day in days:
		line = "%s\t%d" % (day, day_times[day])
		log.WriteLog("day_times", line)


def main():
	make_profit_dir()

	trade_rec_file = "1.txt"
	if len(sys.argv) > 1:
		trade_rec_file = sys.argv[1]

	# 读取交易记录
	records = read_records(trade_rec_file)
	if len(records) == 0:
		raise Exception('cant read trading record!')
		return

	pos_manager = positions.PositionsManager()

	# 分析交易收益
	infos = parse_records(pos_manager, records)

	# 计算每日净值
	calc_day_profit(infos["contracts"].keys(), infos["day_profit"], infos["day_contracts"], infos["day_accountID"], infos["day_times"])

	print "----------------"
	log.WriteLog("result", "合约\t平仓收益\t手续费")
	for c,v in infos["contracts"].items():
		log.WriteLog("result" ,"%s\t%.2f\t%.2f"%(c, v[0], v[1]))


if __name__ == '__main__':
	main()