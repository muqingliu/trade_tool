#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re

def read_origin_data(file_name, num=-1):
	list_data = []
	index = num
	f = open(file_name, "rt")
	if f:
		l = f.readline()
		while l:
			try:
				ma = re.findall("(\d+)/(\d+)/(\d+)-(\d+):(\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)\t(\d+\.\d+)$", l)
				if ma:
					y = ma[0][0]
					m = ma[0][1]
					d = ma[0][2]
					h = ma[0][3]
					mm= ma[0][4]
					_open = ma[0][5]
					_hith = ma[0][6]
					_low  = ma[0][7]
					_close= ma[0][8]
					_num  = ma[0][9]
					list_data.append([y,m,d,h,mm,_open,_hith,_low,_close,_num])
				else:
					print "line %d not match!" % (num -index)

			except Exception, e:
				print e
			l = f.readline()
			index -=1
			if num != -1 and index <=0: break
		f.close()

	return list_data