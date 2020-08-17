import os
import re
import sys
import ConfigParser
import pyetc
import matplotlib.pyplot as plt

def LoadMargin(full_filename):
	data_info = {}

	date_set = []
	profit_set = []
	netvalue_set = []
	margin_set = []
	margin_rate_set = []
	drawdown_set = []

	fp = open(full_filename, "rb")
	if fp:
		init_equity = 0
		max_equity = 0
		min_equity = 1.7976931348623157e+308
		
		line = fp.readline()
		while line:
			res = re.findall("(\d+)-\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
			if res:
				date_str = res[0][0]
				date_set.append(date_str)

				profit = float(res[0][1])
				profit_set.append(profit)

				equity = float(res[0][2])
				if 0 == init_equity:
					init_equity = equity
				netvalue = equity / init_equity
				netvalue_set.append(netvalue)

				if equity > max_equity:
					max_equity = equity
					min_equity = equity
				if equity < min_equity:
					min_equity = equity
				if max_equity > 0:
					equity_drawdown = (max_equity - min_equity) / max_equity
					drawdown_set.append(equity_drawdown)

				margin = float(res[0][3])
				margin_set.append(margin)

				margin_rate = float(res[0][4])
				margin_rate_set.append(margin_rate)

			line = fp.readline()
		fp.close()

	data_info["date"] = date_set
	data_info["init_equity"] = init_equity
	data_info["profit"] = profit_set
	data_info["netvalue"] = netvalue_set
	data_info["drawdown"] = drawdown_set
	data_info["margin"] = margin_set
	data_info["margin_rate"] = margin_rate_set

	return data_info

def LoadCloseEquity(full_filename):
	data_info = {}

	date_set = []
	profit_set = []
	margin_rate_set = []
	drawdown_set = []

	fp = open(full_filename, "rb")
	if fp:
		init_equity = 0
		max_equity = 0
		min_equity = 1.7976931348623157e+308

		line = fp.readline()
		while line:
			res = re.findall("(\d+)-\S+\s+(\S+)\s+(\S+)", line)
			if res:
				date_str = res[0][0]
				date_set.append(date_str)

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
					drawdown_set.append(equity_drawdown)

				profit = float(res[0][2])
				profit_set.append(profit)

				#margin_rate = float(res[0][3])
				#margin_rate_set.append(margin_rate)

			line = fp.readline()
		fp.close()

	data_info["date"] = date_set
	data_info["init_equity"] = init_equity
	data_info["close_profit"] = profit_set
	data_info["drawdown"] = drawdown_set
	#data_info["margin_rate"] = margin_rate_set

	return data_info

def float_range(start,stop,steps):
    return [start+float(i)*(stop-start)/(float(steps)-1) for i in range(steps)]

def ProducePicOnly(figure, dirname, symbol, main_axis, sub_axis, data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix):
	date_set = data_info["date"]
	main_data_set = data_info[main_axis]
	sub_data_set = data_info[sub_axis]

	date_size = len(date_set)
	x = range(date_size)
	y1 = main_data_set
	y2 = sub_data_set

	#画出网格
	plt.grid()

	#主坐标
	ax_main = figure.add_subplot(111)
	#折线图
	ax_main.plot(x, y1, color="red", label=main_axis)
	#图例位置，2为左上角
	ax_main.legend(bbox_to_anchor = (0.14,1.1))
	#主坐标y坐标轴取消科学计数法					
	ax_main.ticklabel_format(style="plain", axis='y')

	#设置主坐标轴X轴样式，刻度为字符串，需特殊处理
	#X轴刻度数量
	if scale_num_x <= 0:
		scale_num_x = 61
	#X轴实际值为0——date_size-1，刻度为每隔date_size/(scale_num_x)打印一个
	area_x = range(0, date_size, date_size/(scale_num_x))
	#X坐标轴上实际显示的刻度名称数组
	scale_x_set = []
	for i in area_x:
		scale_x_set.append(date_set[i])
	#设置X坐标轴样式
	plt.xticks(area_x, scale_x_set, rotation=90)

	#设置主坐标轴Y轴样式，刻度为数字，设置间隔即可
	#获取Y轴值范围
	ylim_main = ax_main.get_ylim()
	#Y轴刻度数量
	if scale_num_y <= 0:
		scale_num_y = 21
	#创建刻度数组
	area_y_main = float_range(ylim_main[0], ylim_main[1], scale_num_y)
	#设置Y坐标轴样式
	plt.yticks(area_y_main)

	#副坐标
	ax_sub = ax_main.twinx()
	#柱状图 参数alpha指透明度，0为完全透明，1为完全不透明
	ax_sub.bar(x, y2, 1, alpha=bar_alpha, color=bar_color, linewidth=0, label=sub_axis)
	#图例位置，1为右上角
	ax_sub.legend(bbox_to_anchor = (1,1.1))
	#副坐标y坐标轴取消科学计数法
	ax_sub.ticklabel_format(style="plain", axis='y')

	#设置副坐标轴Y轴样式，刻度为数字，设置间隔即可
	#获取Y轴值范围
	ylim_sub = ax_sub.get_ylim()
	#创建刻度数组
	area_y_sub = float_range(ylim_sub[0], ylim_sub[1], scale_num_y)
	#若为百分比刻度
	if area_y_sub[1] < 1:
		#创建百分比刻度
		scale_y_set = []
		for y_sub_value in area_y_sub:
			scale_y_set.append("%.2f%%" % (y_sub_value * 100))
		#设置Y坐标轴样式
		plt.yticks(area_y_sub, scale_y_set)
	#若为普通数值刻度
	else:
		#设置Y坐标轴样式
		plt.yticks(area_y_sub)

	if (len(symbol) > 0):
		#设置标题
		plt.title("%s(%d)"%(symbol, data_info["init_equity"]))
		tar_pic_name = "%s\\%s_%s_%s%s.png" % (dirname, symbol, main_axis, sub_axis, suffix)
	else:
		#设置标题
		plt.title("total(%d)"%(data_info["init_equity"]))
		tar_pic_name = "%s\\%s_%s%s.png" % (dirname, main_axis, sub_axis, suffix)

	#保存图片
	plt.savefig(tar_pic_name)
	#清空画板
	plt.clf()
	

def ProduceMarginPic(figure, dirname, symbol, full_filename, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix):
	#读取数据
	data_info = LoadMargin(full_filename)
	#利润保证金图
	ProducePicOnly(figure, dirname, symbol, "profit", "margin", data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix)
	#净值保证金图
	ProducePicOnly(figure, dirname, symbol, "netvalue", "margin", data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix)
	#利润回撤图
	ProducePicOnly(figure, dirname, symbol, "profit", "drawdown", data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix)
	#净值回撤图
	ProducePicOnly(figure, dirname, symbol, "netvalue", "drawdown", data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix)
	#利润保证金率图
	ProducePicOnly(figure, dirname, symbol, "profit", "margin_rate", data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix)
	#净值保证金率图
	ProducePicOnly(figure, dirname, symbol, "netvalue", "margin_rate", data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix)

def ProduceProfitPic(figure, dirname, symbol, full_filename, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix):
	#读取数据
	data_info = LoadCloseEquity(full_filename)
	##平仓盈利保证金率图
	#ProducePicOnly(figure, dirname, symbol, "close_profit", "margin_rate", data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix)
	#平仓盈利回撤图
	ProducePicOnly(figure, dirname, symbol, "close_profit", "drawdown", data_info, bar_alpha, bar_color, scale_num_x, scale_num_y, suffix)

def find_tar_pre_suffix(statistic_path):
	pre_end_index = statistic_path.find("statistic", 0)
	if -1 == pre_end_index:
		return ("", "")

	suffix_end_index = statistic_path.rfind(".log", 0)
	if -1 == suffix_end_index:
		return ("", "")

	pre = statistic_path[0:pre_end_index]
	suffix = statistic_path[pre_end_index+9:suffix_end_index]

	return (pre, suffix)

def main():
	config = pyetc.load(r'system.ini')

	#创建公共画板，每画一幅便要重新创建一块画板会降低速度
	fig = plt.figure(figsize=(int(config.pic_width)/80, int(config.pic_height)/80))

	# 首先通过根目录statistic文件找出目标文件前缀，再在各个目录中寻找标的文件解析（前提：先遍历根目录）
	main_pre = ""
	for root,dirs,files in os.walk(config.path):
		if len(dirs) > 0:
			for file in files:
				if file.find("statistic", 0) != -1 and file.find(".log", 0) != -1:
					pre_suffix = find_tar_pre_suffix(file)
					if cmp(main_pre, "") == 0:
						main_pre = pre_suffix[0]

					tar_margin_file = "%s\\%smargin%s.log" % (root, main_pre, pre_suffix[1])
					tar_profit_file = "%s\\%sclose_equity%s.log" % (root, main_pre, pre_suffix[1])

					if os.path.exists(tar_margin_file):
						ProduceMarginPic(fig, root, "", tar_margin_file, float(config.bar_alpha), config.bar_color, int(config.scale_num_x), int(config.scale_num_y), pre_suffix[1])
					if os.path.exists(tar_profit_file):
						ProduceProfitPic(fig, root, "", tar_profit_file, float(config.bar_alpha), config.bar_color, int(config.scale_num_x), int(config.scale_num_y), pre_suffix[1])
		else:
			index = root.rfind("\\", 0)
			symbol = root[index+1:]

			for file in files:
				if file.find("statistic", 0) != -1 and file.find(".log", 0) != -1:
					pre_suffix = find_tar_pre_suffix(file)

					tar_margin_file = "%s\\%smargin%s.log" % (root, main_pre, pre_suffix[1])
					tar_profit_file = "%s\\%sclose_equity%s.log" % (root, main_pre, pre_suffix[1])

					if os.path.exists(tar_margin_file):
						ProduceMarginPic(fig, root, symbol, tar_margin_file, float(config.bar_alpha), config.bar_color, int(config.scale_num_x), int(config.scale_num_y), pre_suffix[1])
					if os.path.exists(tar_profit_file):
						ProduceProfitPic(fig, root, symbol, tar_profit_file, float(config.bar_alpha), config.bar_color, int(config.scale_num_x), int(config.scale_num_y), pre_suffix[1])

	#关闭画板
	plt.close()

if __name__ == '__main__':
	main()