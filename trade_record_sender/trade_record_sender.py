import httppost
import pyetc
import re
import time
import log
from xml.dom.minidom import Document

def compare_data(data1, data2):
	sys1 = int(data1[8])
	sys2 = int(data2[8])

	if data1[1] > data2[1]:
		return 1
	elif data1[1] == data2[1] and sys1 > sys2:
		return 1

	return -1

def read_file(filename):
	list_data = []
	try:
		index = 1
		f = open(filename, "rb")
		if f:
			line = f.readline()
			while line:
				ma = re.search("\S+\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
				if ma:
					arrs = ma.groups()
					date = int(arrs[0])
					hh = int(arrs[1])
					mm = int(arrs[2])
					ss = int(arrs[3])
					contract = arrs[4]
					trade_dir = arrs[5].decode('gbk')
					trade_type = arrs[6].decode('gbk')
					price = float(arrs[7])
					trade_num = int(arrs[8])
					commission = float(arrs[9])
					touji = arrs[10]
					sysID = arrs[11]

					list_data.append([contract, date%1000000, hh*10000+mm*100+ss, trade_dir, trade_type, price, trade_num, commission, sysID])
				else:
					print "line %d not match!" % (index)

				index = index + 1

				line = f.readline()
			f.close()
	except Exception, msg:
		print_log(u"error:%s" % (msg))

	return list_data

def produce_xml(brokerID, userID, report_name, list_data, max_send_num, lastest_date_str, lastest_sys_id_str):
	doc = Document()

	root_ele = doc.createElement('root')
	doc.appendChild(root_ele)

	trader_ele = doc.createElement('trader1')
	root_ele.appendChild(trader_ele)

	time_ele = doc.createElement('time')
	cur_time = time.time()
	time_text = doc.createTextNode("%u" % cur_time)
	time_ele.appendChild(time_text)
	trader_ele.appendChild(time_ele)

	name_ele = doc.createElement("name")
	name_text = doc.createTextNode(report_name)
	name_ele.appendChild(name_text)
	trader_ele.appendChild(name_ele)

	broker_id_ele = doc.createElement("brokerID")
	broker_id_text = doc.createTextNode(brokerID)
	broker_id_ele.appendChild(broker_id_text)
	trader_ele.appendChild(broker_id_ele)

	user_id_ele = doc.createElement("userID")
	user_id_text = doc.createTextNode(userID)
	user_id_ele.appendChild(user_id_text)
	trader_ele.appendChild(user_id_ele)

	lastest_date = int(lastest_date_str)
	lastest_sys_id = int(lastest_sys_id_str)

	index = 0
	size = len(list_data)
	for i in xrange(0,size):
		data = list_data[i]
		date = data[1]
		sys_id = int(data[8])

		if date < lastest_date or (date == lastest_date and sys_id <= lastest_sys_id):
			continue

		if index < int(max_send_num):
			trade_rec_ele = doc.createElement("trade_rec%u" % (index + 1))
			trader_ele.appendChild(trade_rec_ele)

			produce_tr_xml(doc, trade_rec_ele, data)

			index = index + 1
		else:
			break

	result = doc.toprettyxml(indent = '')

	return (result, index)

def produce_tr_xml(doc, trade_rec_ele, data):
	contract_ele = doc.createElement("contract")
	contract_text = doc.createTextNode(data[0])
	contract_ele.appendChild(contract_text)
	trade_rec_ele.appendChild(contract_ele)

	sys_ele = doc.createElement("sys_id")
	sys_text = doc.createTextNode(data[8])
	sys_ele.appendChild(sys_text)
	trade_rec_ele.appendChild(sys_ele)

	trade_date_ele = doc.createElement("trade_date")
	trade_date_text = doc.createTextNode("%u" % data[1])
	trade_date_ele.appendChild(trade_date_text)
	trade_rec_ele.appendChild(trade_date_ele)

	trade_time_ele = doc.createElement("trade_time")
	trade_time_text = doc.createTextNode("%u" % data[2])
	trade_time_ele.appendChild(trade_time_text)
	trade_rec_ele.appendChild(trade_time_ele)

	buy_type_ele = doc.createElement("buy_type")
	buy_type_text = doc.createTextNode(data[4])
	buy_type_ele.appendChild(buy_type_text)
	trade_rec_ele.appendChild(buy_type_ele)

	buy_dir_ele = doc.createElement("buy_dir")
	buy_dir_text = doc.createTextNode(data[3])
	buy_dir_ele.appendChild(buy_dir_text)
	trade_rec_ele.appendChild(buy_dir_ele)

	price_ele = doc.createElement("price")
	price_text = doc.createTextNode("%f" % data[5])
	price_ele.appendChild(price_text)
	trade_rec_ele.appendChild(price_ele)

	profit_ele = doc.createElement("profit")
	profit_text = doc.createTextNode("0.00")
	profit_ele.appendChild(profit_text)
	trade_rec_ele.appendChild(profit_ele)

	total_profit_ele = doc.createElement("total_profit")
	total_profit_text = doc.createTextNode("0.00")
	total_profit_ele.appendChild(total_profit_text)
	trade_rec_ele.appendChild(total_profit_ele)

	commission_ele = doc.createElement("commission")
	commission_text = doc.createTextNode("%f" % data[7])
	commission_ele.appendChild(commission_text)
	trade_rec_ele.appendChild(commission_ele)

	number_ele = doc.createElement("number")
	number_text = doc.createTextNode("%u" % data[6])
	number_ele.appendChild(number_text)
	trade_rec_ele.appendChild(number_ele)

def post_report(url, data):
	return httppost.httpPost(url, data)  

def send_info(brokerID, userID, report_name, max_send_num, list_trade_record, trade_rec_report_url):
	try:
		if -1 == trade_rec_report_url.find("http://"):
			trade_rec_report_url = "http://" + trade_rec_report_url

		result = produce_xml(brokerID, userID, report_name, [], max_send_num, "0", "0")
		buf = post_report(trade_rec_report_url, result[0])

		result_list = []
		for trade_record_path in list_trade_record:
			list_data = read_file(trade_record_path)
			result_list.extend(list_data)

		result_list_new = sorted(result_list, cmp=compare_data)

		while len(buf) == 16:
			date_str = buf[0:6]
			sys_id_str = buf[6:]

			result = produce_xml(brokerID, userID, report_name, result_list_new, max_send_num, date_str, sys_id_str)
			if result[1] > 0:
				content = result[0].decode("utf8")
				content = content.encode("gb2312")
				buf = post_report(trade_rec_report_url, content)
			else:
				break
	except Exception, msg:
		print_log(u"error:%s" % (msg))

def print_log(msg):
    log.set_log_mode('a')

    now_datetime = time.localtime()
    content = u"%u-%02u-%02u %02u:%02u:%02u %s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, 
    	now_datetime.tm_hour, now_datetime.tm_min, now_datetime.tm_sec, msg)
    log.WriteLog("sys", content)

def main():
	try:
		config = pyetc.load(r'sys.conf')
		for info in config.info_set:
			send_info(info["brokerID"], info["userID"], info["report_name"], config.max_send_num, info["table_record_path"], 
				config.trade_rec_report_url)
	except Exception, msg:
		print_log(u"error:%s" % (msg))

if __name__ == '__main__':
	main()