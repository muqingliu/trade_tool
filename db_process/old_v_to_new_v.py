import os
import re

def read_file(file_name):
    list_data = []
    f = open(file_name, "rt")
    if f:
        l = f.readline()
        while l:
            try:
                ma = re.findall("(\w+)\s(\d+)\s(\d+)\s(\d+)\s(\d+\.\d+)\s(-*\d+\.\d+)\s(\d+\.\d+)\s(\d+)$", l)
                if ma:
                    contract = ma[0][0]
                    minute = int(ma[0][1])
                    buy_type = int(ma[0][2])
                    buy_dir = int(ma[0][3])
                    price = float(ma[0][4])
                    profit = float(ma[0][5])
                    commission = float(ma[0][6])
                    number  = float(ma[0][7])
                    list_data.append([contract,minute,buy_type,buy_dir,price,profit,commission,number])
            except Exception, e:
                print e
            l = f.readline()
        f.close()

    return list_data

def translate_to_db(new_file_name, list_data):
	f = open(new_file_name, "wt")
	if f:
		for data in list_data:
			buy_type_str = "开仓"
			if data[2] == 1:
				buy_type_str = "平仓"

			buy_dir_str = "买入"
			if data[3] == 1:
				buy_dir_str = "卖出"

			content = "%d\t%02d:%02d:00\t%s\t%s\t%s\t%f\t%d\t%f\n" % (20000000+data[1]/10000,data[1]%10000/100,data[1]%100,data[0],\
				buy_dir_str,buy_type_str,data[4],data[7],data[6])

			f.write(content)

		f.close()

def main():
	list_data = read_file("trade_records_zjq.db")
	
	translate_to_db("trade_records_new_zjq.db", list_data)

if __name__ == '__main__':
	main()