import contract_info
import log

DIR_BUY  = 0
DIR_SELL = 1
TYPE_OPEN = 0
TYPE_CLOSE = 1

def GetSymbol(contract):
	str_len = len(contract)
	for i in xrange(0,str_len):
		if contract[i] >= '0' and contract[i] <= '9':
			return contract[0:i]

	return contract

class Position(object):
	def __init__(this, contract, datetime, dir, number, price):
		this.contract = contract
		this.datetime = datetime
		this.dir = dir
		this.number = number 
		this.price = price

class PositionsManager(object):
	def __init__(this):
		this.contracts = {}
		this.total_profit  = {}
		this.total_commission = {}
		this.date_profit = {}

	def open(this, datetime, contract, dir, number, price, commission):
		if not this.contracts.has_key(contract): 
			this.contracts[contract] = {}
			this.contracts[contract][DIR_BUY] = []
			this.contracts[contract][DIR_SELL] = []

		this.contracts[contract][dir].append(Position(contract, datetime, dir, number, price))

		if not this.total_profit.has_key(contract): 
			this.total_profit[contract] = 0
			this.total_commission[contract] = commission
		else:
			this.total_commission[contract] += commission

	def close(this, datetime, contract, dir, number, price, commission, today):
		if not this.contracts.has_key(contract): 
			err = 'sell error, not match contract[%s] date[%s] dir[%s] number[%s] price[%.2f]' %  (contract, datetime, dir, number, price)
			log.WriteError(err)
			raise Exception, err
			return
		date = datetime/1000000

		if not this.date_profit.has_key(contract): this.date_profit[contract] = {}
		if not this.date_profit[contract].has_key(date): this.date_profit[contract][date] = 0

		total_profit_1 = 0
		total_sell = number
		positions = this.contracts[contract][1-dir]
		index = 0
		this_profit = 0
		while True:
			if len(positions) == 0: break
			pos = positions[index]

			#print contract, datetime
			if today and pos.datetime/1000000 != datetime/1000000: # 如果是平今，但是该仓非今仓
				loop_count = 0
				while True:
					index += 1
					loop_count += 1
					pos = positions[index]
					if pos.datetime/1000000 == datetime/1000000: break
					if loop_count > 500:
						err = 'sell error, cant find close today position [%s] date[%s] dir[%s] number[%s] price[%.2f]' %  (contract, datetime, dir, number, price)
						raise Exception, err

			remove_number = min(pos.number, total_sell)
			profit = 0
			if dir == DIR_SELL:
				profit += remove_number * (price - pos.price) * contract_info.get_contract_mul(contract)
			else:
				profit += remove_number * (pos.price - price) * contract_info.get_contract_mul(contract)
			total_profit_1 += profit

			this_profit += profit
			
			total_sell -= remove_number
			pos.number -= remove_number

			if pos.number == 0: positions.remove(pos)			
			if total_sell == 0: break

		this.total_profit[contract] += this_profit
		this.date_profit[contract][date] += this_profit

		if total_sell > 0: 
			err ='sell error, not match contract[%s] date[%s] dir[%s] number[%s] price[%.2f]' %  (contract, datetime, dir, number, price)
			log.WriteError(err)
			raise Exception, err
			return
		# 手续费累加
		this.total_commission[contract] += commission

		return this_profit
	
	def get_profit(this, contract):
		if not this.total_profit.has_key(contract): raise Exception, 'must trade before get_profit'
		return this.total_profit[contract]

	def get_commission(this, contract):
		if not this.total_commission.has_key(contract): raise Exception, 'must trade before get_commission'
		return this.total_commission[contract]

	def get_pos_price(this, contract, pos_dir):
		if not this.contracts.has_key(contract): raise Exception, 'must trade before get_pos_price'
		dir_positions = this.contracts[contract]
		if len(dir_positions[pos_dir]) == 0:
			return 0

		pos_price = 0
		number = 0
		for pos in dir_positions[pos_dir]:
			pos_price += pos.price * pos.number
			number += pos.number

		return pos_price / number

	def get_pos_profit(this, contract, date, query_price_func):
		if not this.contracts.has_key(contract): raise Exception, 'must trade before get_pos_price'
		dir_positions = this.contracts[contract]
		pos_profit = 0
		if len(dir_positions[DIR_BUY]) > 0 or len(dir_positions[DIR_SELL]) > 0:
			price = query_price_func(contract, date)
			for pos in dir_positions[DIR_BUY]:
				pos_profit += (price - pos.price) * pos.number * contract_info.get_contract_mul(contract)

			for pos in dir_positions[DIR_SELL]:
				pos_profit += (pos.price - price) * pos.number * contract_info.get_contract_mul(contract)

		return pos_profit

	def get_position_profit(this, date, query_price_func):
		day_profits ={}
		position_profits = {}
		for contract, dir_positions in this.contracts.items():
			#if len(dir_positions[DIR_BUY]) == 0 and len(dir_positions[DIR_SELL]) == 0: continue
			if not position_profits.has_key(contract): position_profits[contract] = 0

			if len(dir_positions[DIR_BUY]) > 0 or len(dir_positions[DIR_SELL]) > 0:
				price = query_price_func(contract, date)
				buy_position_price = 0
				sel_position_price = 0
				buy_number = 0
				sel_number = 0
				for pos in dir_positions[DIR_BUY]:
					position_profits[contract] += (price - pos.price) * pos.number * contract_info.get_contract_mul(contract)
					buy_position_price += pos.price * pos.number
					buy_number += pos.number

				for pos in dir_positions[DIR_SELL]:
					position_profits[contract] += (pos.price - price) * pos.number * contract_info.get_contract_mul(contract)
					sel_position_price += pos.price * pos.number
					sel_number += pos.number

				if buy_number > 0: buy_position_price /= buy_number
				if sel_number > 0: sel_position_price /= sel_number

				# print "position price %s %.2f - %.2f %.2f" % (date, price, buy_position_price, sel_position_price)
				# if this.date_profit.has_key(contract) and this.date_profit[contract].has_key(date):
				# 	print "dateprofit %d %.2f" % (date, this.date_profit[contract][date])

			if not day_profits.has_key(contract): day_profits[contract] = 0
			day_profits[contract] += position_profits[contract] + this.total_profit[contract] - this.total_commission[contract]
			
		return day_profits, position_profits

	def get_margin(this, date, query_price_func):
		day_margin = 0
		for contract, dir_positions in this.contracts.items():	
			if len(dir_positions[DIR_BUY]) > 0 or len(dir_positions[DIR_SELL]) > 0:
				price = query_price_func(contract, date)
				for pos in dir_positions[DIR_BUY]:
					day_margin += price * pos.number * contract_info.get_contract_mul(contract) * contract_info.get_contract_mar(contract)

				for pos in dir_positions[DIR_SELL]:
					day_margin += price * pos.number * contract_info.get_contract_mul(contract) * contract_info.get_contract_mar(contract)

		return day_margin

	def print_position(this):
		log.WriteLog("result", "--------------------")
		log.WriteLog("result", "print position")
		for contract, dir_positions in this.contracts.items():
			if len(dir_positions[DIR_BUY]) > 0 or len(dir_positions[DIR_SELL]) > 0:
				buy_position_price = 0
				sel_position_price = 0
				buy_number = 0
				sel_number = 0
				for pos in dir_positions[DIR_BUY]:
					buy_position_price += pos.price * pos.number
					buy_number += pos.number
					log.WriteLog("result", "hold\t%s\t[buy]\t%d-%06d\t%.2f\t%d" %(contract, pos.datetime/1000000, pos.datetime%1000000, pos.price, pos.number))

				for pos in dir_positions[DIR_SELL]:
					sel_position_price += pos.price * pos.number
					sel_number += pos.number
					log.WriteLog("result", "hold\t%s\t[sell]\t%d-%06d\t%.2f\t%d" %(contract, pos.datetime/1000000, pos.datetime%1000000, pos.price, pos.number))

				log.WriteLog("result", "------------------static")
				if buy_number > 0: 
					buy_position_price /= buy_number
					log.WriteLog("result", "%s\t[buy]\t%d\t%.2f" %(contract, buy_number, buy_position_price))
				if sel_number > 0: 
					sel_position_price /= sel_number
					log.WriteLog("result", "%s\t[sell]\t%d\t%.2f" %(contract, sel_number, sel_position_price))

				log.WriteLog("result", "\n")
