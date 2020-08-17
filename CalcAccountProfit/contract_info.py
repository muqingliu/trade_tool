import re
import exchange_config
import log
import os

g_exg_config = None
g_contract_mul = {}
g_contract_mar = {}

# 获取交易所
def create_exg_config():
	global g_exg_config 
	if not g_exg_config:
		path_ini = "exchange.ini"
		g_exg_config = exchange_config.exchange_config(path_ini)
	return g_exg_config

def get_contract_symbol(contract):
	m = re.match("(\D+)\d*", contract)
	return m.groups()[0]

def load_contract_mul():
	file_name = "contract_mul.ini"
	if not os.path.exists(file_name):
		err = "file [%s] doesn't exist" %  file_name
		log.WriteError(err)
		raise Exception, err
		return

	file = open(file_name, "rt")
	if not file: 
		err = 'cant open file [%s]' %  file_name
		log.WriteError(err)
		raise Exception, err
		return
	global g_contract_mul
	line = file.readline()
	while line:
		try:
			ma = re.search("(\S+)\s+(\S+)", line)
			if ma:
				arrs = ma.groups()				
				contract = arrs[0]
				mul = int(arrs[1])
				g_contract_mul[contract]=mul
			else:
				log.WriteError("%s line %d not match!" % (file_name, index))
		except Exception, e:
			print e

		line = file.readline()
	file.close()

def get_contract_mul(contract):
	symbol = get_contract_symbol(contract)
	if not g_contract_mul.has_key(symbol):
		log.WriteError("%s isn't in contract_mul.ini" % contract)
		return None
	return g_contract_mul[symbol]

def load_contract_mar():
	file_name = "contract_mar.ini"
	if not os.path.exists(file_name):
		err = "file [%s] doesn't exist" %  file_name
		log.WriteError(err)
		raise Exception, err
		return

	file = open(file_name, "rt")
	if not file: 
		err = 'cant open file [%s]' %  file_name
		log.WriteError(err)
		raise Exception, err
		return

	global g_contract_mar
	line = file.readline()
	while line:
		try:
			ma = re.search("(\S+)\s+(\S+)", line)
			if ma:
				arrs = ma.groups()				
				contract = arrs[0]
				mar = float(arrs[1]) / 1000
				g_contract_mar[contract]=mar
			else:
				log.WriteError("%s line %d not match!" % (file_name, index))
		except Exception, e:
			print e

		line = file.readline()
	file.close()

def get_contract_mar(contract):
	symbol = get_contract_symbol(contract)
	if not g_contract_mar.has_key(symbol):
		log.WriteError("%s isn't in contract_mar.ini" % contract)
		return None
	return g_contract_mar[symbol]