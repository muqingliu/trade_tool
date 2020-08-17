import sys,re
import log


def read_records(trade_rec_file):
	file_name = trade_rec_file
	list_data = []
	index = 1
	f = open(file_name, "rt")
	if not f: 
		err = 'cant open file [%s]' %  file_name
		raise Exception(err)
		return
		
	line = f.readline()
	while line:
		index += 1
		try:
			ma = re.match("(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)\s+(\S+)$", line)
			if ma:
				arrs = ma.groups(0)
				trade_type = arrs[0]#.decode('gbk')
				date = int(arrs[1])
				hh = int(arrs[2])
				mm = int(arrs[3])
				ss = int(arrs[4])
				trade_num = int(arrs[5])
				trade_dir = arrs[6]#.decode('gbk')

				list_data.append([date, hh*10000+mm*100+ss, trade_dir, trade_type, trade_num])
			else:
				print("line %d not match!" % (index))

		except Exception as e:
			print(e)

		line = f.readline()
	f.close()
	return list_data


def sort_rec(records):
	records_buy = []
	records_sel = []

	for rec in records:
		if rec[3] == "建仓" and rec[2] == "买入": records_buy.append(rec)
		elif (rec[3] == "平仓" or rec[3] == "平今") and rec[2] == "卖出": records_buy.append(rec)
		elif rec[3] == "建仓" and rec[2] == "卖出": records_sel.append(rec)
		elif (rec[3] == "平仓" or rec[3] == "平今") and rec[2] == "买入": records_sel.append(rec)

	return records_buy, records_sel


def process_record(records):
	if len(records) == 0: return

	def is_close_rec(element):
		return (element[3] == "平仓" or  element[3] == "平今")

	close_recs = []
	idx_end = len(records)-1
	while True:
		# print(idx_end)
		if idx_end <= 0: break
		element = records[idx_end]
		if is_close_rec(element):
			pre_element = records[idx_end-1]
			if is_close_rec(pre_element):
				close_recs.append(element)
				del records[idx_end]
				idx_end -= 1
			else:
				#print(records[idx_end], records[idx_end-1])
				del records[idx_end]
				del records[idx_end-1]
				idx_end -= 2
		else:
			if len(close_recs) > 0:
				#print(close_recs[len(close_recs)-1], records[idx_end])

				close_recs.pop()
				del records[idx_end]
				idx_end -= 1
			else:
				idx_end -= 1


def main():
	trade_rec_file = "3.txt"
	if len(sys.argv) > 1:
		trade_rec_file = sys.argv[1]

	# 读取交易记录
	records = read_records(trade_rec_file)
	if len(records) == 0:
		raise Exception('cant read trading record!')
		return
	
	rec_buy, rec_sel = sort_rec(records)

	process_record(rec_buy)
	process_record(rec_sel)
	
	out = open("2.txt", "w")
	for r in rec_buy:
		out.write(" ".join(r))
		out.write("\n")

	b = ""
	for r in rec_sel:
		b = b.join(str(r))
		
	out.write(b)
	out.write("\n")

	out.close()

if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		log.WriteError(e)
		import traceback
		print(traceback.print_exc())