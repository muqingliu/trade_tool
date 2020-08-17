import log
import scanf
import os

def walk_sub_dir(cur_dir, sub_dir):
	map_report_per_area = {}
	sub_path = cur_dir + '\\' + sub_dir
	for root, dirs, files in os.walk(sub_path):
		for file_name in files:
			file_path = root + '\\' + file_name

			fp = open(file_path, "rb")
			if None == fp:
				log.WriteError ('%s can\'t be opened' % file_path)
				continue

			empty_index_first = file_name.find(' ')
			empty_index_second = file_name.find(' ', empty_index_first + 1)
			date = file_name[empty_index_first + 1 : empty_index_second]

			map_report_per_area[date] = {}

			line = fp.readline()
			while(len(line) > 0):
				user_info = scanf.sscanf(line, "%s %s %s %s %s %d %s %d %d %d")

				key = "android%u" % (user_info[7])
				if 53 == user_info[8]:
					key = "java%u" % (user_info[7])

				if map_report_per_area[date].has_key(key):
					map_report_per_area[date][key] = map_report_per_area[date].get(key) + 1
				else:
					map_report_per_area[date][key] = 1

				line = fp.readline()

			fp.close()

	return map_report_per_area

def create_report(cur_dir, map_report):
	file_report_path = cur_dir + '\\' + "reprot.txt"
	fp = open(file_report_path, "wb")
	if None == fp:
		return

	for area in map_report.keys():
		area_str = "%sarea" % area
		fp.write(area_str)
		fp.write('\n')

		map_report_per_area = map_report[area]
		for date in map_report_per_area.keys():
			fp.write(date)
			fp.write(':')

			for key in map_report_per_area[date].keys():
				content = "%s:%d\t" % (key, map_report_per_area[date].get(key))
				fp.write(content)

			fp.write('\n')

		fp.write('\n')

	fp.close()

if __name__ == '__main__':
	cur_dir = os.getcwd()

	map_report = {}
	map_report["total"] = {}
	for root, dirs, files in os.walk(cur_dir):
		for dir_name in dirs:
			map_report_per_area = walk_sub_dir(root, dir_name)
			map_report[dir_name] = map_report_per_area

			for date in map_report_per_area.keys():
				if not map_report["total"].has_key(date):
					map_report["total"][date] = {}

				for key in map_report_per_area[date].keys():
					if map_report["total"][date].has_key(key):
						map_report["total"][date][key] = map_report["total"][date][key] + map_report_per_area[date][key]
					else:
						map_report["total"][date][key] = map_report_per_area[date][key]

	create_report(cur_dir, map_report)