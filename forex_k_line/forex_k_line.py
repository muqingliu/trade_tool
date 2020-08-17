import re
import os

def ReadFile(filename):
	print filename
	fp = open(filename, "rb")
	if fp:
		k_data_set = []
		line = fp.readline()
		while line:
			res = re.findall("\w+,(\d+),(\d+),(\d+.\d+),(\d+.\d+),(\d+.\d+),(\d+.\d+),(\d+)", line)
			if res:
				date = int(res[0][0])
				time = int(res[0][1])
				o = float(res[0][2])
				h= float(res[0][3])
				l = float(res[0][4])
				c = float(res[0][5])
				volume = int(res[0][6])

				k_data_set.append([date%1000000*10000+time/100,o,h,l,c,volume])

			line = fp.readline()
		fp.close()

	return k_data_set
		
def process_forex_file(contract, k_data_set):
	filename = "%sL0.txt" % contract
	fp = open(filename, "wb")
	for k_data in k_data_set:
		time_str = "%u/%02u/%02u-%02u:%02u" % (2000+k_data[0]/100000000,k_data[0]/1000000%100,k_data[0]/10000%100,k_data[0]/100%100,
			k_data[0]%100)
		fp.write("%s\t%f\t%f\t%f\t%f\t%d\n" % (time_str,k_data[1],k_data[2],k_data[3],k_data[4],k_data[5]))
	fp.close()

def main():
	for root,dirs,files in os.walk("forex"):
		for filename in files:
			index = filename.find(".")
			contract = filename[0:index]
			ext = filename[index+1:]
			if ext != "txt":
				continue

			fullpath = os.path.join(root,filename)
			k_data_set = ReadFile(fullpath)
			process_forex_file(contract, k_data_set)

if __name__ == '__main__':
	main()