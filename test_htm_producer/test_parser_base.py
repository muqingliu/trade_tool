template ="""
<!DOCTYPE html>
<head>
    <meta charset="utf-8">
    <title><<!!contract>></title>
</head>
<h2><<!!contract>></h2>
<body>
	<<!!linkbutton>>
    <!-- 为ECharts准备一个具备大小（宽高）的Dom -->
    <div id="main1" style="width:1620px; height:400px"></div>
    <div id="main2" style="width:1620px; height:400px"></div>
    <div id="main3" style="width:1620px; height:400px"></div>
    <div id="main4" style="width:1620px; height:400px"></div>
    <div id="main5" style="width:1620px; height:400px"></div>
    <div id="main6" style="width:1620px; height:400px"></div>
    <div id="main7" style="width:1620px; height:400px"></div>
    <!-- ECharts单文件引入 -->
    <script src="../../js/echarts.js"></script>
    <script src="../../js/common_echart.js"></script>
	<link rel="stylesheet" type="text/css" href="../../css/default.css">
	<link rel="stylesheet" type="text/css" href="../../css/easyui.css">
	<script type="text/javascript" src="../../js/jquery.min.js"></script>
	<script type="text/javascript" src="../../js/jquery.easyui.min.js"></script>
    <script type="text/javascript">
        // 使用
        chart_draw_line_bar(echarts, "main1", "利润保证金图", "利润", "保证金率", [<<!!xAxis>>], <<!!series1>>);
        chart_draw_line_bar(echarts, "main2", "利润回撤图", "利润", "回撤", [<<!!xAxis>>], <<!!series2>>);
        chart_draw_line_bar_color(echarts, "main3", "平仓保证金率图", "平仓利润", "保证金率", [<<!!xAxis>>], <<!!pieces>>, <<!!series3>>);
        chart_draw_line_bar_color(echarts, "main4", "平仓回撤图", "平仓利润", "平仓回撤", [<<!!xAxis>>], <<!!pieces>>, <<!!series4>>);
        chart_draw_double_bar(echarts, "main5", "盈利周期图", ["回调天数","回补天数"], "天数", [<<!!xAxis1>>], <<!!series5>>);
        chart_draw_double_bar(echarts, "main6", "顺序回撤图", ["回撤","当前回撤"], "百分比", [<<!!xAxis2>>], <<!!series6>>);
        chart_draw_bar(echarts, "main7", "月度收益图", "单月收益", [<<!!xAxis3>>], <<!!series7>>);
    </script>
</body>
"""


import json
import time
import log
import re
import os
import sys
import pyetc
import copy


if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def print_log(msg):
    log.set_log_mode('a')

    now_datetime = time.localtime()
    content = u"%u-%02u-%02u %02u:%02u:%02u %s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, now_datetime.tm_hour, 
              now_datetime.tm_min, now_datetime.tm_sec, msg)
    log.WriteLog("sys", content)


def parse_date(date):
	m = re.findall("(\d{6})-(\d{2}):(\d{2})",date)
	if m:
		return [int(d) for d in m[0]]
	return []


class TestParserBase(object):
	"""docstring for TestParserBase"""
	def __init__(self):
		super(TestParserBase, self).__init__()


	def find_test_path(self, rootdir):
		test_tool_dirs = []
		for parent,dirnames,filenames in os.walk(rootdir):
			if parent == rootdir:
				test_tool_dirs.extend(dirnames)

		timestamp = time.time()
		st_time = time.gmtime(timestamp)

		map_test_file = {}

		map_contract_full_path = {}
		for test_tool_dir in test_tool_dirs:
			test_tool_full_path = os.path.join(rootdir,test_tool_dir)
			test_tool_full_log_path = "%s\\log\\%04d-%d" % (test_tool_full_path,st_time.tm_year,st_time.tm_mon)
			test_tool_full_db_path = "%s\\db" % test_tool_full_path

			for parent,dirnames,filenames in os.walk(test_tool_full_log_path):
				for dirname in dirnames:
					contract = dirname
					contract_full_log_path = "%s\\%s\\%s" % (test_tool_full_log_path, contract, contract)
					if not map_contract_full_path.has_key(contract):
						map_contract_full_path[contract] = {}
					map_contract_full_path[contract]["log"] = contract_full_log_path

			for parent,dirnames,filenames in os.walk(test_tool_full_db_path):
				for dirname in dirnames:
					contract = dirname
					contract_full_db_path = "%s\\%s" % (test_tool_full_db_path, contract)
					if not map_contract_full_path.has_key(contract):
						map_contract_full_path[contract] = {}
					map_contract_full_path[contract]["db"] = contract_full_db_path

		return map_contract_full_path


	def judge_test_file(self, contract, parent, filename, map_test_file):
		file_word_list = filename.split('_')
		if filename.find("margin") >= 0 and file_word_list[0] != contract:
			full_file_path = os.path.join(parent,filename)
			map_test_file[contract]["margin"] = full_file_path

		if filename.find("close_equity") >= 0 and file_word_list[0] != contract:
			full_file_path = os.path.join(parent,filename)
			map_test_file[contract]["close_equity"] = full_file_path

		if filename.find("round_trip") >= 0:
			full_file_path = os.path.join(parent,filename)
			map_test_file[contract]["round_trip"] = full_file_path

		if filename.find("statistic") >= 0:
			full_file_path = os.path.join(parent, filename)
			map_test_file[contract]["statistic"] = full_file_path

		if filename.find("trade_records.db") >= 0:
			full_file_path = os.path.join(parent,filename)
			map_test_file[contract]["trade_record"] = full_file_path


	def find_test_file(self, rootdir):
		map_test_file = {}
		map_contract_full_path = self.find_test_path(rootdir)
		for contract in map_contract_full_path.keys():
			contract_full_log_path = map_contract_full_path[contract]["log"]
			for parent,dirnames,filenames in os.walk(contract_full_log_path):
				if not map_test_file.has_key(contract):
					map_test_file[contract] = {}

				for filename in filenames:
					self.judge_test_file(contract, parent, filename, map_test_file)

			contract_full_db_path = map_contract_full_path[contract]["db"]
			for parent,dirnames,filenames in os.walk(contract_full_db_path):
				if not map_test_file.has_key(contract):
					map_test_file[contract] = {}

				for filename in filenames:
					self.judge_test_file(contract, parent, filename, map_test_file)

		return map_test_file


	def get_web_path(self, rootdir, policy, contract):
		full_path = os.path.join(rootdir,policy)
		if not os.path.exists(full_path):
			os.makedirs(full_path)

		full_path = "%s\\%s.htm" % (full_path, contract)
		return full_path


	def read_margin(self, filename):
		datas = [[],[],[],[],[]]
		with open(filename, 'rb') as f:
			line = f.readline()
			while line:
				eles = line.split('\t')
 				time = parse_date(eles[0])
				profit = float(eles[1])
				equity = float(eles[2])
				margin_rate = float(eles[4])
				retract = float(eles[6])

				datas[0].append(eles[0])
				datas[1].append(profit)
				datas[2].append(equity)
				datas[3].append(margin_rate)
				datas[4].append(retract)
				line = f.readline()

		return datas


	def calc_month_profit(self, times, profits):
		datas_month_profit = [[],[]]
		last_month = cur_month = times[0][0:4]
		last_total_profit = cur_total_profit = profits[0]
		for i,time in enumerate(times):
			cur_month = time[0:4]
			cur_total_profit = profits[i]
			if cur_month != last_month:
				datas_month_profit[0].append(last_month)
				datas_month_profit[1].append(cur_total_profit - last_total_profit)
				last_month = cur_month
				last_total_profit = cur_total_profit
		datas_month_profit[0].append(last_month)
		datas_month_profit[1].append(cur_total_profit - last_total_profit)
		return datas_month_profit


	def sort_time_retract_pairs(self, times, retracts):
		if len(times) != len(retracts):
			return

		cur_time = times[len(times) - 1]
		cur_retract = retracts[len(retracts) - 1]
		time_retract_pairs = []
		for i,time in enumerate(times):
			retract = retracts[i]
			# if equitys[i] > max_equity:
			# 	max_equity = equitys[i]
			# 	retract = 0
			# 	cur_time = time
			# 	cur_retract = 0
			# else:
			# 	if max_equity != 0:
			# 		retract = (max_equity - equitys[i]) / max_equity
			# 	else:
			# 		retract = 0

			# 	if retract > cur_retract:
			# 		cur_time = time
			# 		cur_retract = retract
			time_retract_pair = (time,retract)
			time_retract_pairs.append(time_retract_pair)

		new_time_retract_pairs = sorted(time_retract_pairs, key=lambda time_retract:time_retract[1], reverse=True)

		tar_retraces = []
		new_times = []
		new_retraces = []
		for i,time_retract_pair in enumerate(new_time_retract_pairs):
			if cur_time == time_retract_pair[0]:
				tar_retraces.append(time_retract_pair[1])
			else:
				tar_retraces.append(0)
			new_times.append(time_retract_pair[0])
			new_retraces.append(time_retract_pair[1])

		return (tar_retraces, new_times, new_retraces)


	def read_close_equity(self, filename):
		datas = [[],[],[]]
		with open(filename, "rb") as fp:
			init_equity = 0
			max_equity = 0
			min_equity = 1.7976931348623157e+308

			line = fp.readline()
			while line:
				res = re.findall("(\d+)-\S+\s+(\S+)\s+(\S+)", line)
				if res:
					date_str = res[0][0]
					datas[0].append(date_str)

					equity = float(res[0][1])
					if 0 == init_equity:
						init_equity = equity

					if equity > max_equity:
						max_equity = equity
						min_equity = equity
					if equity < min_equity:
						min_equity = equity
					if max_equity > 0:
						equity_drawdown = (max_equity - min_equity) / max_equity
						datas[2].append(equity_drawdown)

					profit = float(res[0][2])
					datas[1].append(profit)

				line = fp.readline()

		return datas


	def calc_pos_from_trade_records(self, filename):
		positions_by_date = {}
		last_date = 0
		with open(filename, 'rb') as f:
			line = f.readline()
			while line:
				eles = line.split('\t')
				date = int(eles[0]) % 1000000
				time_info = eles[1].split(':')
				time = int(time_info[0]) * 10000 + int(time_info[1]) * 100 + int(time_info[0])
				cur_min = date % 1000000 * 10000 + time / 100
				contract = eles[2]
				dir_str = eles[3].decode("gbk")
				dir = 0 if dir_str == u"买入" else 1
				type_str = eles[4].decode("gbk")
				type = 0 if type_str == u"开仓" else 1
				num = int(eles[6])

				if not positions_by_date.has_key(date):
					positions_by_date[date] = {}

					contract_buy = "%s_0" % contract
					contract_sell = "%s_1" % contract
					positions_by_date[date][contract_buy] = 0 if last_date == 0 else positions_by_date[last_date][contract_buy]
					positions_by_date[date][contract_sell] = 0 if last_date == 0 else positions_by_date[last_date][contract_sell]

				if type == 0:
					if dir == 0:
						positions_by_date[date][contract_buy] = positions_by_date[date][contract_buy] + num
					else:
						positions_by_date[date][contract_sell] = positions_by_date[date][contract_sell] + num
				else:
					if dir == 0:
						positions_by_date[date][contract_sell] = max(positions_by_date[date][contract_sell] - num, 0)
					else:
						positions_by_date[date][contract_buy] = max(positions_by_date[date][contract_buy] - num, 0)

				last_date = date

				line = f.readline()

		return positions_by_date


	def get_profit_pieces_markdatas(self, set_close_equity, contract, positions_by_date):
		pieces = []
		markdatas = []
		markdatabegin = {}
		markdataend = {}
		close_equity_dates = set_close_equity[0]
		close_equity_profits = set_close_equity[1]
		begin_index = 0
		cur_color = 'gray'
		contract_buy_num = 0
		contract_sell_num = 0
		index_date = 0
		last_close_equity_profit = 0
		is_delay = False
		for i,close_equity_date_str in enumerate(close_equity_dates):
			close_equity_date = int(close_equity_date_str)
			close_equity_profit = float(close_equity_profits[i])

			#交易第二日再次检查净值是否增长（注意因为前一日平仓当前已不再持仓了）
			if is_delay:
				if last_close_equity_profit != 0 and close_equity_profit > last_close_equity_profit:
					markdataend["xAxis"] = "%s-00:00" % close_equity_date_str
					markdatabeginnew = copy.deepcopy(markdatabegin)
					markdataendnew = copy.deepcopy(markdataend)
					markdatapair = [markdatabeginnew, markdataendnew]
					markdatas.append(markdatapair)

				is_delay = False

			#若当日有持仓
			if positions_by_date.has_key(close_equity_date):
				index_date = close_equity_date

				#（默认同时仅有一个方向持仓）当仓位方向发生变化时（持多仓变持空仓或无持仓，持空仓变持多仓或无持仓，无持仓变持多仓或持空仓），
				# 记录染色曲线段
				contract_buy = "%s_0" % contract
				contract_sell = "%s_1" % contract
				if contract_buy_num > 0 and positions_by_date[index_date][contract_buy] == 0 \
					or contract_buy_num == 0 and positions_by_date[index_date][contract_buy] > 0 \
					or contract_sell_num == 0 and positions_by_date[index_date][contract_sell] > 0 \
					or contract_sell_num > 0 and positions_by_date[index_date][contract_sell] == 0:
					piece = {}
					if begin_index > 0:
						piece['gt'] = begin_index
					piece['lte'] = i
					if cur_color != None:
						piece['color'] = cur_color
					pieces.append(piece)

					begin_index = i

				#持仓期间，若盈利则该染为粉红色
				#起始时间为开仓时
				if contract_buy_num == 0 and positions_by_date[index_date][contract_buy] > 0 \
					or contract_sell_num == 0 and positions_by_date[index_date][contract_sell] > 0:
					markdatabegin["xAxis"] = "%s-00:00" % close_equity_date_str

				#结束时间为平仓时，检查净值是否增长
				if contract_buy_num > 0 and positions_by_date[index_date][contract_buy] == 0 \
					or contract_sell_num > 0 and positions_by_date[index_date][contract_sell] == 0:
					markdataend["xAxis"] = "%s-00:00" % close_equity_date_str

					if last_close_equity_profit != 0 and close_equity_profit > last_close_equity_profit:
						markdataend["xAxis"] = "%s-00:00" % close_equity_date_str
						markdatabeginnew = copy.deepcopy(markdatabegin)
						markdataendnew = copy.deepcopy(markdataend)
						markdatapair = [markdatabeginnew, markdataendnew]
						markdatas.append(markdatapair)
					elif close_equity_profit == last_close_equity_profit:
						#净值的变化可能要在交易第二天才显示出来，因此当平仓当天净值未变时，还需检查下一交易日
						is_delay = True

				#持多仓曲线为红，持空仓曲线为绿，无持仓曲线无需染色
				contract_buy_num = positions_by_date[index_date][contract_buy]
				contract_sell_num = positions_by_date[index_date][contract_sell]
				if contract_buy_num > 0:
					cur_color = 'red'
				elif contract_sell_num > 0:
					cur_color = 'green'
				else:
					cur_color = 'gray'

			last_close_equity_profit = close_equity_profit

		piece = {}
		piece['gt'] = begin_index
		if cur_color != None:
			piece['color'] = cur_color
		pieces.append(piece)

		return (pieces,markdatas)


	def read_round_trip(self, filename):
		datas = [[],[],[]]
		with open(filename, "rb") as fp:
			line = fp.readline()
			while line:
				res = re.findall("(\d+)\t\d+\t\d+\t(\d+)\t(\d+)", line)
				if res:
					date_str = res[0][0]
					datas[0].append(date_str)

					lost_days = int(res[0][1]) + int(res[0][2])
					datas[1].append(lost_days)

					cover_up_days = res[0][2]
					datas[2].append(cover_up_days)

				line = fp.readline()

		return datas


	def read_statistic(self, filename):
		datas = {}
		with open(filename, "rb") as fp:
			key = ""
			line = fp.readline()
			while line:
				line = line.decode("gbk")
				if line != '\r\n':
					size = len(line)
					sub_line = " "
					for i in xrange(0,size):
						if line[size - 1 - i] == '\r' or line[size - 1 - i] == '\n':
							line = line[0:size - 1 - i]
							line = line + sub_line
							sub_line = sub_line + " "
						else:
							break

					if line.find(u"总数据") >= 0:
						key = "total"
						datas[key] = []
					elif line.find(u"年份") >= 0:
						size = len(line)
						tar_index = -1
						for i in xrange(0,size):
							if line[i] >= '0' and line[i] <= '9':
								tar_index = i
								break

						key = line[tar_index:]
						key = key.rstrip(" ")
						datas[key] = []

					datas[key].append(line)

				line = fp.readline()

		return datas
		

	def create_statistic(self, datas_statistic):
		statistic_btn_str = ""
		keys = datas_statistic.keys()
		keys.sort()
		for key in keys:
			statistic_infos = datas_statistic[key]
			statistic_btn_str += "<div style=\"display:inline-block;\"><div style=\"margin:20px 0 10px 0;\">"
			statistic_btn_str += "<a href=\"#\" class=\"easyui-linkbutton\" onclick=\"javascript:$('#%s').panel('open')\">%s</a></div>" % (key, key)
			statistic_btn_str += "<div id=\"%s\" class=\"easyui-panel\" title=\"Basic Panel\" data-options=\"iconCls:'icon-save'," % (key)
			statistic_btn_str += " closable:true\" closed=true style=\"width:300px;height:200px;padding:10px;\">"
			statistic_btn_str += "<ul>"
			for statistic_info in statistic_infos:
				statistic_btn_str += "<li>%s</li>" % (statistic_info)
			statistic_btn_str += "</ul></div></div>"

		return statistic_btn_str


	def create_result_web(self, template, contract, map_test_file):
		#解析净值和保证金文件
		datas_margin = self.read_margin(map_test_file["margin"])
		dates_margin = ["'" + e + "'" for e in datas_margin[0]]

		#设置每日净值横坐标
		dates_margin_str = (',').join(dates_margin)
		content = template.replace('<<!!xAxis>>', dates_margin_str)

		#替换标题字段
		content = content.replace('<<!!contract>>', contract)

		#解析盈亏统计情况文件
		datas_statistic = self.read_statistic(map_test_file["statistic"])
		#建立每年和总盈亏按钮
		statistic_btn_str = self.create_statistic(datas_statistic)

		content = content.replace('<<!!linkbutton>>', statistic_btn_str)

		#解析平仓净值文件
		datas_close_equity = self.read_close_equity(map_test_file["close_equity"])
		#解析交易记录文件
		positions_by_date = self.calc_pos_from_trade_records(map_test_file["trade_record"])
		#获得平仓曲线染色部分
		pieces_markdatas = self.get_profit_pieces_markdatas(datas_close_equity, contract, positions_by_date)

		content = content.replace('<<!!pieces>>', json.dumps(pieces_markdatas[0]))

		#设置盈亏周期图横坐标
		datas_round_trip = self.read_round_trip(map_test_file["round_trip"])
		dates_round_trip = ["'" + e + "'" for e in datas_round_trip[0]]

		dates_round_trip_str = (',').join(dates_round_trip)
		content = content.replace('<<!!xAxis1>>', dates_round_trip_str)

		#对回撤进行从大到小排序
		sorted_pairs = self.sort_time_retract_pairs(dates_margin, datas_margin[4])
		cur_retracts = sorted_pairs[0]
		sorted_times = sorted_pairs[1]
		sorted_retracts = sorted_pairs[2]

		#设置孙婿回撤图横坐标
		sorted_times_retrace_str = (',').join(sorted_times)
		content = content.replace('<<!!xAxis2>>', sorted_times_retrace_str)

		#从每日净值中算出每月盈亏
		datas_month_profit = self.calc_month_profit(datas_margin[0], datas_margin[1])
		#设置每月盈亏横坐标
		months_month_profit = ["'" + e + "'" for e in datas_month_profit[0]]

		months_month_profit_str = (',').join(months_month_profit)
		content = content.replace('<<!!xAxis3>>', months_month_profit_str)

		series_profit = {'name':'利润',
					'type':'line',
					'symbolSize' : '0',
					'yAxis' : 1, 
					'data':datas_margin[1],
					}

		series_margin_rate = {'name':'保证金率',
					'type':'bar',
					'symbolSize' : '0',
					'yAxisIndex' : 1,
					'data':datas_margin[3],
					}

		series_retrace = {'name':'回撤',
					'type':'bar',
					'symbolSize' : '0',
					'yAxisIndex' : 1,
					'data':datas_margin[4],
					}

		series_close_equity = {'name':'平仓利润',
					'type':'line',
					'symbolSize' : '0',
					'yAxis' : 1, 
					'data':datas_close_equity[1],
					'markArea' : { 'itemStyle' : { 'normal': { 'color' : 'pink' } }, 'data' : pieces_markdatas[1]}
					}

		series_close_margin_rate = {'name':'保证金率',
					'type':'bar',
					'symbolSize' : '0',
					'yAxisIndex' : 1,
					'data':datas_margin[3],
					}

		series_close_retrace = {'name':'平仓回撤',
					'type':'bar',
					'symbolSize' : '0',
					'yAxisIndex' : 1,
					'data':datas_close_equity[2],
					}

		series_lost = {'name':'回调天数',
					'type':'bar',
					'symbolSize' : '0',
					'data':datas_round_trip[1],
					}

		series_cover_up = {'name':'回补天数',
					'type':'bar',
					'symbolSize' : '0',
					'data':datas_round_trip[2],
					}

		retrace_color_1_str = "function (params){" \
			"return 'rgb(151,255,255)';" \
		"}"

		retrace_color_2_str = "function (params){" \
			"return 'rgb(255,0,0)';" \
		"}"

		series_sorted_retrace = {'name':'回撤',
					'type':'bar',
					'symbolSize' : '0',
					'barWidth' :1,
					'data':sorted_retracts,
					'itemStyle': {   
						'normal':{  
							'color': "<<!!retrace_color1>>"
						}
					}
				}

		series_target_retrace = {'name':'当前回撤',
					'type':'bar',
					'symbolSize' : '0',
					'barWidth' :1,
					'data':cur_retracts,
					'itemStyle': {   
						'normal':{  
							'color': "<<!!retrace_color2>>"
						}
					}
				}

		series_month_profit = {'name':'单月收益',
					'type':'bar',
					'symbolSize' : '0',
					'data':datas_month_profit[1],
					}

		series1 = [series_margin_rate, series_profit]
		content = content.replace('<<!!series1>>', json.dumps(series1))

		series2 = [series_retrace, series_profit]
		content = content.replace('<<!!series2>>', json.dumps(series2))

		series3 = [series_close_margin_rate, series_close_equity]
		content = content.replace('<<!!series3>>', json.dumps(series3))

		series4 = [series_close_retrace, series_close_equity]
		content = content.replace('<<!!series4>>', json.dumps(series4))

		series5 = [series_lost, series_cover_up]
		content = content.replace('<<!!series5>>', json.dumps(series5))

		series6 = [series_sorted_retrace, series_target_retrace]
		content = content.replace('<<!!series6>>', json.dumps(series6))
		content = content.replace("\"<<!!retrace_color1>>\"", retrace_color_1_str)
		content = content.replace("\"<<!!retrace_color2>>\"", retrace_color_2_str)

		series7 = [series_month_profit]
		content = content.replace('<<!!series7>>', json.dumps(series7))

		return content


def main():
    config = pyetc.load(r'system.ini')

    test_parser_model = TestParserBase()
    map_test_file = test_parser_model.find_test_file(config.test_result_path)
    for contract in map_test_file:
        test_result_files = map_test_file[contract]
        if len(test_result_files) == 0:
            continue

        print contract
        content = test_parser_model.create_result_web(template, contract, test_result_files)

        full_result_path = test_parser_model.get_web_path(config.web_path, config.policy, contract)
        f = open(full_result_path, "w+")
        if f:
            f.write(content)
            f.close()