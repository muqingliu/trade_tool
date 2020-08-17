import pandas as pd
import log
import re
import os
import ConfigParser
import datetime
import exchange_config

class SystemConfig(object):
    # 配置文件信息结构
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.limit_values = {}

        options = ini_parser.options("main")
        for option in options:
            self.limit_values[option] = (float)(ini_parser.get("main", option))

def get_tick_filename_info(tick_filename):
	index_pre = tick_filename.find("_")
	index_next = tick_filename.find(".")
	if -1 != index_pre and -1 != index_next:
		contract = tick_filename[0:index_pre]
		trading_day = int(tick_filename[index_pre + 1:index_next])
		return (contract, trading_day)

	return ("", 0)

def add_min(minute, diff_mins):
    datetime_cur = datetime.datetime(2000 + minute/100000000, minute / 1000000 % 100, minute / 10000 % 100, minute / 100 % 100, minute % 100)
    datetime_next = datetime_cur + datetime.timedelta(minutes = diff_mins)
    minute_next = datetime_next.year % 100 * 100000000 + datetime_next.month * 1000000 + datetime_next.day * 10000 + datetime_next.hour * 100 + datetime_next.minute

    return minute_next

def get_trading_day(minute):
	datetime_cur = datetime.datetime(2000 + minute/100000000, minute / 1000000 % 100, minute / 10000 % 100, minute / 100 % 100, minute % 100)
	if datetime_cur.hour >= 8 and datetime_cur.hour <= 16:
		return datetime_cur.year * 10000 + datetime_cur.month * 100 + datetime_cur.day
	elif datetime_cur.hour >= 20:
		datetime_next = datetime_cur + datetime.timedelta(minutes = 1440)
		if datetime_cur.weekday() == 4: #weekday()=4为周五
			datetime_next = datetime_cur + datetime.timedelta(minutes = 4320)
		return datetime_next.year * 10000 + datetime_next.month * 100 + datetime_next.day
	elif datetime_cur.hour >= 0 and datetime_cur.hour <= 3:
		datetime_next = datetime_cur
		if datetime_cur.weekday() == 5: #weekday()=5为周六
			datetime_next = datetime_cur + datetime.timedelta(minutes = 2880)
		return datetime_next.year * 10000 + datetime_next.month * 100 + datetime_next.day
	return datetime_cur.year * 10000 + datetime_cur.month * 100 + datetime_cur.day
			

# def clear_tick_date(date_complex):
# 	return date_complex.replace('/','',2).replace(':','',2).replace('-','',1)

def clear_cvs_tick_date(date_complex):
	date_complex = date_complex.replace('-','',2).replace(' ','',1).replace(':','',2)
	date_complex = date_complex[0:14]
	return date_complex

def clear_min_date(date_complex):
	date_complex = date_complex.replace('/','',2).replace(':','',1).replace('-','',1)
	date_complex = date_complex[2:]
	return date_complex

# def read_tick_file(file_name):
# 	tick_datas = pd.read_table(file_name, header=None, index_col=False)
# 	del tick_datas[0]
# 	tick_datas[2] = tick_datas[2].map(clear_tick_date)

# 	return tick_datas

def read_cvs_tick_file(file_name):
	tick_datas = pd.read_table(file_name, header=None, index_col=False, sep=',', low_memory=False)
	del tick_datas[0]
	tick_datas = tick_datas.drop(0)
	tick_datas[2] = tick_datas[2].map(clear_cvs_tick_date)

	return tick_datas

def read_min_file(file_name):
	min_datas = pd.read_table(file_name, header=None, index_col=False, low_memory=False)
	min_datas[0] = min_datas[0].map(clear_min_date)

	return min_datas

def calc_k1(exg_cfg, tick_datas):
	groupy = tick_datas.groupby(1)
	keys = groupy.groups.keys()

	list_k_datas = []
	for contract in keys:
		ma = re.findall("([^\d]+)[\d]+", contract)
		symbol = ma[0]

		contract_datas = groupy.get_group(contract)
		cur_time = 0
		open_price = 0
		high_price = 0
		low_price = 99999999
		close_price = 0
		volume = 0
		for index,row in contract_datas.iterrows():
			time = row[2]
			if len(time) != 14:
				continue

			minute = int(time[2:12])
			if cur_time == 0:
				cur_time = minute
			elif cur_time != minute:
				cur_time = add_min(cur_time, 1)
				price = float(row[3])

				if exg_cfg.is_in_exchange_time(symbol, 20000000 + cur_time / 10000, cur_time % 10000):
					list_k_datas.append([contract, cur_time, open_price, high_price, low_price, close_price, volume])
				# else:
				# 	log_name = "%s_%u" % (contract, 20000000 + cur_time / 10000)
				# 	log.WriteLog(log_name, "时间戳[%u]数据不在交易时间范围内" % (cur_time))

				cur_time = minute

				open_price = price
				high_price = price
				low_price = price
				close_price = price
				volume = 0

			price = float(row[3])
			if open_price == 0:
				open_price = price
			if price > high_price:
				high_price = price
			if price < low_price:
				low_price = price
			close_price = price
			volume += float(row[7])

		minute = add_min(minute, 1)
		if exg_cfg.is_in_exchange_time(symbol, 20000000 + minute / 10000, minute % 10000):
			list_k_datas.append([contract, minute, open_price, high_price, low_price, close_price, volume]) 
		# else:
		# 	log_name = "%s_%u" % (contract, 20000000 + minute / 10000)
		# 	log.WriteLog(log_name, "时间戳[%u]数据不在交易时间范围内" % (minute))

		# out = "%s.txt" % (contract)
		# f = open(out, "wb")
		# if f:
		# 	for k_data in list_k_datas:
		# 		content = "%u\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\r\n" % (k_data[1], k_data[2], k_data[3], k_data[4], k_data[5], k_data[6])
		# 		f.write(content)
		# 	f.close()

	k_datas = pd.DataFrame(list_k_datas)
	return k_datas

def check_complete_only(contract, k_datas, exg_cfg, tick):
	ma = re.findall("([^\d]+)[\d]+", contract)
	symbol = ma[0]

	is_pre_date = False
	cur_daymin_index = 0
	daymin_set = []
	for index,row in k_datas.iterrows():
		time = row[1]
		if not tick:
			time = int(row[0])
		date = 20000000 + time / 10000
		trading_day = get_trading_day(time)
		if not is_pre_date:
			if date != trading_day:
				daymin_set = exg_cfg.get_contract_daymin(symbol, trading_day)
				is_pre_date = True
		else:
			if date == trading_day:
				daymin_set = exg_cfg.get_contract_daymin(symbol, date)
				is_pre_date = False
				cur_daymin_index = 0

		if cur_daymin_index >= len(daymin_set):
			continue

		daymin = daymin_set[cur_daymin_index]
		if is_pre_date:
			while daymin < 2100 and cur_daymin_index + 1 < len(daymin_set):
				cur_daymin_index = cur_daymin_index + 1
				daymin = daymin_set[cur_daymin_index]

		cur_time = date % 1000000 * 10000 + daymin

		while cur_time < time:
			log_name = "%s_%u" % (contract, 20000000 + cur_time / 10000)
			if tick:
				log.WriteLog(log_name, "tick时间戳[%u]数据缺失" % (cur_time))
			else:
				log.WriteLog(log_name, "min时间戳[%u]数据缺失" % (cur_time))
		
			cur_daymin_index = cur_daymin_index + 1
			if cur_daymin_index >= len(daymin_set):
				break

			daymin = daymin_set[cur_daymin_index]
			cur_time = date % 1000000 * 10000 + daymin

		if cur_time == time:
			cur_daymin_index = cur_daymin_index + 1
				
def check_tick_complete(k_datas, exg_cfg, file_name):
	groupy = k_datas.groupby(0)
	keys = groupy.groups.keys()

	finename_info = get_tick_filename_info(file_name)
	trading_day = finename_info[1]

	for contract in keys:		
		contract_datas = groupy.get_group(contract)
		for index,row in contract_datas.iterrows():
			time = row[1]
			date = 20000000 + time / 10000
			trading_day_new = get_trading_day(time)
			if trading_day_new != trading_day:
				print date,trading_day_new,trading_day

		check_complete_only(contract, contract_datas, exg_cfg, True)

def check_min_complete(contract, k_datas, exg_cfg):
	check_complete_only(contract, k_datas, exg_cfg, False)

def compare_data(k_datas, exg_cfg):
	groupy = k_datas.groupby(0)
	keys = groupy.groups.keys()

	sys_info = SystemConfig("system.ini")

	for contract in keys:
		min_file = "min/%s.txt" % (contract)
		if not os.path.exists(min_file):
			continue

		ma = re.findall("([^\d]+)[\d]+", contract)
		symbol = ma[0]

		# 检查分钟线数据完整性
		min_datas = read_min_file(min_file)
		check_min_complete(contract, min_datas, exg_cfg)

		#遍历分钟数据进行比较
		contract_datas = groupy.get_group(contract)
		cur_contract_data_index = 0
		for index,row in min_datas.iterrows():
			if cur_contract_data_index >= len(contract_datas.index):
				break

			cur_contract_data = contract_datas.iloc[cur_contract_data_index]
			cur_time = int(cur_contract_data[1])

			min_time = int(row[0])
			if min_time < cur_time:
				continue
			
			while cur_time < min_time:
				cur_contract_data_index = cur_contract_data_index + 1
				if cur_contract_data_index >= len(contract_datas.index):
					break

				cur_contract_data = contract_datas.iloc[cur_contract_data_index]
				cur_time = int(cur_contract_data[1])

			if cur_time == min_time:
				if not exg_cfg.at_end_min(symbol, 20000000 + cur_time / 10000, cur_time % 10000):
					open_diff = float(row[1]) - float(cur_contract_data[2])
					high_diff = float(row[2]) - float(cur_contract_data[3])
					low_diff = float(row[3]) - float(cur_contract_data[4])
					close_diff = float(row[4]) - float(cur_contract_data[5])
					if abs(open_diff) > sys_info.limit_values[contract] or abs(high_diff) > sys_info.limit_values[contract] \
						or abs(low_diff) > sys_info.limit_values[contract] or abs(close_diff) > sys_info.limit_values[contract]:
						log_name = "%s_diff" % (contract)
						log.WriteLog(log_name, "时间戳[%u] 开盘差[%.4f] 最高差[%.4f] 最低差[%.4f] 收盘差[%.4f]" % (cur_time, open_diff, 
							high_diff, low_diff, close_diff))

def check_tick(exg_cfg, file_path, file_name):
	tick_datas = read_cvs_tick_file(file_path)
	tick_k_datas = calc_k1(exg_cfg, tick_datas)
	check_tick_complete(tick_k_datas, exg_cfg, file_name)
	compare_data(tick_k_datas, exg_cfg)

def main():
	exg_cfg = exchange_config.exchange_config("Exchange.ini")

	for root,dirs,files in os.walk("tick"):
		for file_name in files:
			tick_filename_info = get_tick_filename_info(file_name)
			contract = tick_filename_info[0]
			min_file = "min/%s.txt" % (contract)
			if not os.path.exists(min_file):
				continue

			file_path = os.path.join(root,file_name)
			check_tick(exg_cfg, file_path, file_name)

if __name__ == '__main__':
	main()