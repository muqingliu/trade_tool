# -*- coding: utf-8 -*-

import os,re

set_contract = ("jd1501", "rb1505", "ru1505", "IF1412", "SR1505", "RM1505", "bb1501")
set_delay_contract = ("ru1505", "SR1505", "jd1501", "rb1505", "RM1505", "bb1501")

def read_top_bottom(file_name):
	dic_date_area = {}

	fp = open(file_name, "rb")
	if fp:
		line = fp.readline()
		while line:
			try:
				ma = re.findall("([^\s]+)[\s]+([^\s]+)[\s]+([^\s]+)[\s]+([^\s]+).+", line)
				date = int(ma[0][0])
				top = float(ma[0][1])
				bottom = float(ma[0][2])
				limit = float(ma[0][3])

				if not dic_date_area.has_key(date):
					date_area = [top, bottom, top - limit, bottom + limit]
					dic_date_area[date] = date_area
			except Exception, e:
				print e

			line = fp.readline()

		fp.close()

	return dic_date_area

def IsCantCalc(contract, hour, minute, second):
	ma = re.findall("([^\d]+)[\d]+", contract)
	symbol = ma[0]
	if symbol == "au" or symbol == "ag" or symbol == "al" or symbol == "cu" or symbol == "zn" or symbol == "pb" \
		or symbol == "j" or symbol == "p" or symbol == "CF" or symbol == "SR" or symbol == "RM" or symbol == "ME" \
		or symbol == "TA":
		if hour == 21 and (minute < 10 or minute == 10 and second < 10):
			return True
	else:
		if hour == 9 and (minute < 10 or minute == 10 and second < 10):
			return True

	return False

def read_slippage(contract, file_name):
	set_traded_info = []

	delay = False
	for delay_contract in set_delay_contract:
		if cmp(contract, delay_contract) == 0:
			delay = True
			break

	fp = open(file_name, "rb")
	if fp:
		line = fp.readline()
		while line:
			try:
				ma = re.findall("([^-]+)-([^:]+):([^:]+):([^:]+)[^\[]+\[[^\[]+\[([^\]]+)[^\[]+\[([^\]]+)[^\[]+\[[^\[]+"
								"\[([^\]]+)[^\[]+\[([^\]]+).+", line)
				date = int(ma[0][0])
				hour = int(ma[0][1])
				minute = int(ma[0][2])
				second = int(ma[0][3])
				switch = ma[0][4].decode("GBK").encode("utf8")
				direct = ma[0][5].decode("GBK").encode("utf8")
				traded_price = float(ma[0][6])
				slippage = float(ma[0][7])

				if delay and IsCantCalc(contract, hour, minute, second):
					line = fp.readline()
					continue

				traded_info = [date, switch, direct, traded_price, slippage]
				set_traded_info.append(traded_info)
			except Exception, e:
				print e

			line = fp.readline()

		fp.close()

	return set_traded_info

def CalcSlippage(contract):
	file_top_bottom = contract + "_top_bottom.log"
	file_slippage = contract + "_slippage.log"
	dic_date_area = read_top_bottom(file_top_bottom)
	set_traded_info = read_slippage(contract, file_slippage)

	file_result = contract + "_result.log"
	fp_result = open(file_result, "wb")

	slippage_open = 0
	count_open = 0
	slippage = 0
	count = 0
	for traded_info in set_traded_info:
		if not dic_date_area.has_key(traded_info[0]):
			continue

		date_area = dic_date_area[traded_info[0]]
		if traded_info[1] == "开":
			if traded_info[2] == "买":
				if fp_result:
					content = "%d\t0\t%.2f\t%.2f\r\n" % (traded_info[0],traded_info[3],date_area[0])
					fp_result.write(content)

				slippage_open = slippage_open + traded_info[3] - date_area[0]
				slippage = slippage + traded_info[3] - date_area[0]
			elif traded_info[2] == "卖":
				if fp_result:
					content = "%d\t1\t%.2f\t%.2f\r\n" % (traded_info[0],traded_info[3],date_area[1])
					fp_result.write(content)

				slippage_open = slippage_open + date_area[1] - traded_info[3]
				slippage = slippage + date_area[1] - traded_info[3]

			count_open = count_open + 1
		else:
			if traded_info[4] < 0:
				slippage = slippage - traded_info[4]
			else:
				slippage = slippage + traded_info[4]

		count = count + 1

	content = "result:%.2f\t%.2f" % (slippage_open / count_open, slippage / count)
	fp_result.write(content)

	return slippage_open / count_open, slippage / count

def main():
	for contract in set_contract:
		slippage_open, slippage = CalcSlippage(contract)
		print "%s:%.2f\t%.2f" % (contract, slippage_open, slippage)

if __name__ == '__main__':
	main()