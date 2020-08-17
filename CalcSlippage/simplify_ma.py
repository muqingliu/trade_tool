# -*- coding: utf-8 -*-

import os,re

policy = "atr_break"

def atr_break_parse_str(src_str):
	ma = re.findall("([^\t]+)\t([\d]+)-[^\t]+\t[^\t]+\t[^\t]+\t([^\t]+)\t[^\t]+\t([^\t]+)\t([^\t]+)\t.+", src_str)
	date = int(ma[0][1])
	limit = float(ma[0][2])
	top = float(ma[0][3])
	bottom = float(ma[0][4])
	return date, limit, top, bottom

def range_break_parse_str(src_str):
	ma = re.findall("([^\s]+)[\s]+([\d]+)-[^\s]+[\s]+[^\s]+[\s]+[\w]+\[([^\]]+)\][\s]+[\w]+\[([^\]]+)\][\s]+[\w]+\[([^\]]+)\].+", src_str)
	date = int(ma[0][1])
	top = float(ma[0][2])
	bottom = float(ma[0][3])
	limit = float(ma[0][4])
	return date, limit, top, bottom

dic_policy_parse = {
	"atr_break" : atr_break_parse_str, 
	"range_break" : range_break_parse_str
}	

def simplify_ma(file_name):
	dic_date_area = {}

	simple_file_name = file_name.replace("_ma", "_top_bottom")

	fp = open(file_name, "rb")
	fp_simple = open(simple_file_name, "wb")
	if fp and fp_simple:
		line = fp.readline()
		while line:
			try:
				date, limit, top, bottom = dic_policy_parse[policy](line)

				if not dic_date_area.has_key(date):
					dic_date_area[date] = True

					content = "%d\t%.2f\t%.2f\t%.2f\r\n" % (date, top, bottom, limit)
					fp_simple.write(content)
			except Exception, e:
				print e

			line = fp.readline()

		fp.close()
		fp_simple.close()

def main():
	root_dir = os.getcwd()
	full_path = root_dir + "\\" + policy
	list_dir = os.listdir(full_path)
	for dir_str in list_dir:
		if dir_str.find("_ma.log") == -1:
			continue

		print dir_str
		simplify_ma(policy + "\\" + dir_str)

if __name__ == '__main__':
	main()