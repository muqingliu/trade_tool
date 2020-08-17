import ConfigParser
import scanf

# path_ini = "../bin/Trader/ini/exchange.ini"

class exchange_info(object):
	def __init__(this):
		# 交易所名称
		this.name = ""
		# 交易所子名称（用以区分交易时间不同的产品）
		this.sub_name = ""
		# 不同阶段
		this.end_date_set = []
		# 不同阶段的交易时间
		this.stage_time = {}
		# 不同阶段的交易分钟数
		this.stage_min_times = {}

class exchange_config(object):
	def __init__(this, path_ini):
		ini_parser = ConfigParser.ConfigParser()
		ini_parser.read(path_ini)

		this.exchg_info = {}
		this.contract_exchg_sub = {}

		for exg_id in xrange(1,20):
			session_name = "Exchange%d" % exg_id
			if not ini_parser.has_section(session_name):
				break

			info = exchange_info()

			# 交易所名字
			info.name = ini_parser.get(session_name, "name")
			info.sub_name = ini_parser.get(session_name, "sub_name")

			for end_date_id in xrange(1,10):
				option_name = "end_date%d" % end_date_id

				if not ini_parser.has_option(session_name, option_name):
					break

				end_date = int(ini_parser.get(session_name, option_name))
				info.end_date_set.append(end_date)
				info.stage_time[end_date] = []
				info.stage_min_times[end_date] = []

				for time_id in xrange(1,10):
					sub_option_name = "time%d%d" % (end_date_id, time_id)

					if not ini_parser.has_option(session_name, sub_option_name):
						break

					time_str = ini_parser.get(session_name, sub_option_name) 
					time_arr = scanf.sscanf(time_str, "%d-%d")
					info.stage_time[end_date].append(time_arr)

					time_tick = this.make_min_time(time_arr[0], time_arr[1])
					info.stage_min_times[end_date].extend(time_tick)

			this.exchg_info[info.sub_name] = info

			for var_id in xrange(1,100):
				option_name = "var%d" % var_id
				if not ini_parser.has_option(session_name, option_name):
					break

				var_name = ini_parser.get(session_name, option_name) 
				this.contract_exchg_sub[var_name] = info.sub_name


	def make_min_time(this, time1, time2):
		time1_H = time1 / 100 % 100
		time2_H = time2 / 100 % 100

		time1_M = time1 % 100
		time2_M = time2 % 100

		times = []
		for x in xrange(time1_H, time2_H + 1):
			for y in xrange(0, 60):
				if x == time1_H and y <= time1_M: continue
				if x == time2_H and y == time2_M+1:
					break

				times.append(x * 100 + y)

		return times

	def get_contract_daymin_count(this, contract, date):
		exg_sub = this.contract_exchg_sub[contract]
		info = this.exchg_info[exg_sub]

		for end_date in info.end_date_set:
			if date < end_date:
				return len(info.stage_min_times[end_date])

		return 0

	def get_contract_daymin(this, contract, date):
		exg_sub = this.contract_exchg_sub[contract]
		info = this.exchg_info[exg_sub]

		for end_date in info.end_date_set:
			if date < end_date:
				return info.stage_min_times[end_date]

		return []

	def get_contract_exchage(this, contract):
		exg_sub = this.contract_exchg_sub[contract]
		info = this.exchg_info[exg_sub]

		return info.name

	def is_night(this, contract):
		is_night = False
		exg_sub = this.contract_exchg_sub[contract]
		info = this.exchg_info[exg_sub]
		for key in info.stage_time.keys():
			if key == 99999999:
				time_arr_list = info.stage_time[key]
				for time_arr in time_arr_list:
					if time_arr[0] == 2100:
						return True

		return False

def test():
	path_ini = "exchange.ini"

	config = exchange_config(path_ini)

	print config.get_contract_daymin_count("RU", 20100611)


if __name__ == '__main__':
	test()	
