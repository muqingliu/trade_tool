import re
import os

def read_file(path):
	set_file = []
	for root,dirs,files in os.walk(path):
		for name in files:
			set_file.append(os.path.join(root,name))

	list_data = []

	for file_name in set_file:
		fp = open(file_name, 'rb')
		if fp:
			index = 0
			content = fp.readline()
			while content:
				index += 1
				try:
					ma = re.findall("(\d+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\S+)\s*,\s*(\S+)\s*,\s*(\d+)\s*,\s*(\d+[\.\d+]*)\s*,\s*(-*\d+[\.\d+]*)\s*,\s*(\d+)\s*,\s*(\S+)\s*,\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", content)
					if ma:
						date = int(ma[0][0])
						accountID = ma[0][1]
						contract = ma[0][2]
						dir = ma[0][3]
						type = ma[0][4]
						number = int(ma[0][5])
						price = float(ma[0][6])
						commission = float(ma[0][7])
						tradeID = int(ma[0][8])
						time = int(ma[0][12])
						list_data.append([date,accountID,contract,dir,type,number,price,commission,tradeID,time])
					else:
						ma = re.findall("(\d+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\S+)\s*,\s*(\S+)\s*,\s*(\d+)\s*,\s*(\d+[\.\d+]*)\s*,\s*(-*\d+[\.\d+]*)\s*,\s*(\d+)\s*,\s*(\S+)\s*,\s*,\s*(\d+)\s*,\s*(\d+)", content)
						if ma:
							date = int(ma[0][0])
							accountID = ma[0][1]
							contract = ma[0][2]
							dir = ma[0][3]
							type = ma[0][4]
							number = int(ma[0][5])
							price = float(ma[0][6])
							commission = float(ma[0][7])
							tradeID = int(ma[0][8])
							time = int(ma[0][11])
							list_data.append([date,accountID,contract,dir,type,number,price,commission,tradeID,time])
						else:
							ma = re.findall("(\d+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\S+)\s*,\s*(\S+)\s*,\s*(\d+)\s*,\s*(\d+[\.\d+]*)\s*,\s*(-*\d+[\.\d+]*)\s*,\s*(\d+)\s*,\s*(\S+)\s*,\s*,\s*(\d+)\s*,\s*,\s*(\d+)", content)
							if ma:
								date = int(ma[0][0])
								accountID = ma[0][1]
								contract = ma[0][2]
								dir = ma[0][3]
								type = ma[0][4]
								number = int(ma[0][5])
								price = float(ma[0][6])
								commission = float(ma[0][7])
								tradeID = int(ma[0][8])
								time = int(ma[0][11])
								list_data.append([date,accountID,contract,dir,type,number,price,commission,tradeID,time])
							else:
								print("line %d not match!" % (index))
				except Exception, e:
					print e
				content = fp.readline()
			fp.close()

	return list_data

def cmp(data1, data2):
	if data1[0] > data2[0]:
		return 1
	elif data1[0] == data2[0]:
		if data1[8] > data2[8]:
			return 1
	
	return -1

def sort_data(list_data):
	list_data = sorted(list_data, cmp)
	return list_data

def main():
	list_data = read_file('data')
	list_data = sort_data(list_data)

	fp = open("merge_data.txt", "wt")
	if fp:
		for data in list_data:
			content = "%d\t%s\t%s\t%s\t%s\t%d\t%f\t%f\t%d\t%d\n" % (data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9])

			fp.write(content)

		fp.close()			

if __name__ == '__main__':
	main()