import os
import re

def read_file(file_name):
    list_data = []
    index = 1
    f = open(file_name, "rt")
    if f:
        l = f.readline()
        while l:
            index += 1
            try:
                ma = re.findall("(\d+)\s(\d+):(\d+):(\d+)\s(\w+)\s(\S+)\s(\S+)\s(\d+[\.\d+]*)\s(\d+)\s(\d+[\.\d+]*)\s(\S+)\s(\d+)\s(\d+)$", l)
                if ma:
                    date = int(ma[0][0])
                    hh = int(ma[0][1])
                    mm = int(ma[0][2])
                    ss = int(ma[0][3])
                    contract = ma[0][4]
                    buy_dir = ma[0][5]
                    buy_type = ma[0][6]
                    price = float(ma[0][7])
                    number = int(ma[0][8])
                    commission = float(ma[0][9])
                    touji = ma[0][10]
                    tradeID = int(ma[0][11])
                    list_data.append([date,hh,mm,ss,contract,buy_dir,buy_type,price,number,commission,touji,tradeID])
                else:
                    print("line %d not match!" % (index))
            except Exception, e:
                print e
            l = f.readline()
        f.close()

    return list_data

def cmp_by_time(data1, data2):
    if data1[0] > data2[0]:
        return 1
    elif data1[0] == data2[0]:
        time1 = data1[1] * 10000 + data1[2] * 100 + data1[3]
        time2 = data2[1] * 10000 + data2[2] * 100 + data2[3]
        if (time1 >= 200000 and time2 >= 200000) or (time1 < 200000 and time2 < 200000):
            if time1 >= time2:
                return 1
        elif time1 < 200000 and time2 >= 200000:
            return 1

    return -1

def sort_trade_records(list_data, new_file_name):
    list_data_new = sorted(list_data, cmp=cmp_by_time)

    f = open(new_file_name, "wt")
    if f:
        for data in list_data_new:
            content = "%d\t%02d:%02d:%02d\t%s\t%s\t%s\t%f\t%d\t%f\t%s\t%d\n" % (data[0],data[1],data[2],data[3],data[4],data[5],\
                data[6],data[7],data[8],data[9],data[10],data[11])

            f.write(content)

        f.close()

def main():
    list_data = read_file("trade_records.db")

    sort_trade_records(list_data, "trade_records_new.db")

if __name__ == '__main__':
	main()