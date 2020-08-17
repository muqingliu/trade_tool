#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os,re
import common

def calc_total_equity(dicEquity, file_name):
	first = False
	final_date = 0
	keys = dicEquity.keys()
	size = len(keys)
	if size == 0:
		first = True
	else:
		keys.sort()
		final_date = keys[size - 1]

	init_equity = 0
	last_date = 0
	last_profit = 0
	last_equity = 0
	last_margin = 0
	f_equity = open(file_name, "rb")
	if f_equity:
		l_equity = f_equity.readline()
		while l_equity:
			ma = re.findall("[^\t]+\t(\d+)-[^\t]+\t([^\t]+)\t([^\t]+)\t([^\t]+).*$", l_equity)
			if ma:
				_date = int(ma[0][0])
				_profit = float(ma[0][1])
				_equity = float(ma[0][2])
				_margin = float(ma[0][3])

				if 0 == init_equity:
					init_equity = _equity

				if last_date > 0:
					right_cur_date = common.AddDay(last_date, 1)
					while right_cur_date < _date:
						if dicEquity.has_key(right_cur_date):
							dicEquity[right_cur_date][0] += last_profit
							dicEquity[right_cur_date][1] += last_equity - init_equity
							dicEquity[right_cur_date][2] += last_margin
						else:
							dicEquity[right_cur_date] = [last_profit, last_equity, last_margin]

						right_cur_date = common.AddDay(right_cur_date, 1)

				if not first:
					if _date > final_date:
						break
					else:
						if dicEquity.has_key(_date):
							dicEquity[_date][0] += _profit
							dicEquity[_date][1] += _equity - init_equity
							dicEquity[_date][2] += _margin
						else:
							dicEquity[_date] = [_profit, _equity, _margin]
				else:
					dicEquity[_date] = [_profit, _equity, _margin]

				last_date = _date
				last_profit = _profit
				last_equity = _equity
				last_margin = _margin
			else:
				print "%s line %d not match!" % (_path,index)

			l_equity = f_equity.readline()

		f_equity.close()

	keys = dicEquity.keys()
	keys.sort()
	for _date in keys:
		if _date > last_date:
			del dicEquity[_date]


def merge_equity(path):
	dicEquity = {}
	for parent,dirnames,filenames in os.walk(path): 
		for filename in filenames:
			index = filename.find("margin")
			if index != -1:
				fullname = os.path.join(parent, filename)
				calc_total_equity(dicEquity, fullname)

	f_equity = open("total_equity.txt", "wb")
	if f_equity:
		keys = dicEquity.keys()
		keys.sort()
		for key in keys:
			_profit = dicEquity[key][0]
			_equity = dicEquity[key][1]
			_margin = dicEquity[key][2]
			_margin_rate = 0
			if _equity > 0:
				_margin_rate = _margin / _equity

			content = "%d\t%.2f\t%.2f\t%.2f\t%.2f\r\n" % (key, _profit, _margin_rate, _margin, _equity)
			f_equity.write(content)

	f_equity.close()

def main():
	merge_equity("./equity")

if __name__ == '__main__':
	main()