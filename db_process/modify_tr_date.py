import re
import os
import datetime

def read_tr(filename):
    list_tr = []
    with open(filename, "rt") as f:
        l = f.readline()
        while l:
            try:
                list_data = l.split('\t')
                print list_data
                list_tr.append(list_data)
            except Exception, e:
                print e

            l = f.readline()

    return list_tr

def modify_tr_date(list_tr, filename):
	with open(filename, "wt") as f:
		for tr in list_tr:
			yyyymmdd = int(tr[0])
			list_hhmmss = tr[1].split(':')
			hh = int(list_hhmmss[0])
			mm = int(list_hhmmss[1])
			ss = int(list_hhmmss[2])

			st_date = datetime.date(yyyymmdd / 10000, yyyymmdd / 100 % 100, yyyymmdd % 100)
			st_time = datetime.time(hh, mm, ss)

			if hh >= 20:
				if st_date.isoweekday() == 1:
					st_date = st_date - datetime.timedelta(days = 3)
				else:
					st_date = st_date - datetime.timedelta(days = 1)
			elif hh >= 0 and hh <= 3:
				if st_date.isoweekday() == 1:
					st_date = st_date - datetime.timedelta(days = 2)

			date_str_new = "%04u%02u%02u" % (st_date.year,st_date.month,st_date.day)
			f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (date_str_new,tr[1],tr[2],tr[3],tr[4],tr[5],tr[6],tr[7],tr[8],tr[9]))

def main():
	list_data = read_tr("trade_records.db")
	modify_tr_date(list_data, "trade_records_new.db")

if __name__ == '__main__':
	main()