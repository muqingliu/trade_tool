DIR_BUY  = 0
DIR_SELL = 1
TYPE_OPEN = 0
TYPE_CLOSE = 1

mutil_set = {
	"CNJ16" : 1,
	"FDAX_DEC_16" : 25,
	"FDAX_JUN_16" : 25,
	"FDAX_SEP_16" : 25,
	"HSIJ16" : 50,
	"HSIK16" : 50,
	"HSIM16" : 50,
	"HSIN16" : 50,
	"HSIU16" : 50,
	"HSI1607" : 50,
	"CL_1607" : 1000,
	"CL_1608" : 1000,
	"CL1608" : 1000,
	"CL1609" : 1000,
	"MINI_SP_1606" : 50,
	"MINI_SP_1609" : 50,
	"DAX_1606" : 25,
	"DAX_1609" : 25,
	"FDAX1609" : 25,
	"OI609" : 10,
	"ru1609" : 10,
	"SR609" : 10,
	"ni1609" : 10,
	"hc1610" : 10,
	"CF609" : 5,
	"a1609" : 10,
	"m1609" : 10,
	"rb1610" : 10,
	"cu1608" : 5,
	"sn1609" : 10,
	"au1612" : 1000,
	"v1609" : 5,
	"pp1609" : 5,
	"i1609" : 100,
	"GC1608" : 100
}

price_tick_set = {
	"CNJ16" : 2.5,
	"FDAX_DEC_16" : 0.5,
	"FDAX_JUN_16" : 0.5,
	"FDAX_SEP_16" : 0.5,
	"HSIJ16" : 1,
	"HSIK16" : 1,
	"HSIM16" : 1,
	"HSIN16" : 1,
	"HSIU16" : 1,
	"HSI1607" : 1,
	"CL_1607" : 0.01,
	"CL_1608" : 0.01,
	"CL1608" : 0.01,
	"CL1609" : 0.01,
	"MINI_SP_1606" : 0.25,
	"MINI_SP_1609" : 0.25,
	"DAX_1606" : 0.5,
	"DAX_1609" : 0.5,
	"FDAX1609" : 0.5,
	"OI609" : 2,
	"ru1609" : 5,
	"SR609" : 1,
	"ni1609" : 1,
	"hc1610" : 2,
	"CF609" : 0.5,
	"a1609" : 1,
	"m1609" : 1,
	"rb1610" : 1,
	"cu1608" : 0.5,
	"sn1609" : 1,
	"au1612" : 0.05,
	"v1609" : 5,
	"pp1609" : 1,
	"i1609" : 0.5,
	"GC1608" : 0.1
}

multi_factor = {
	"FDAX_DEC_16" : 1.1128,
	"FDAX_JUN_16" : 1.1128,
	"FDAX_SEP_16" : 1.1128,
	"HSIJ16" : 0.1286,
	"HSIK16" : 0.1286,
	"HSIM16" : 0.1286,
	"HSIN16" : 0.1286,
	"HSIU16" : 0.1286,
	"HSI1607" : 0.1286,
	"CL_1607" : 1,
	"CL_1608" : 1,
	"CL1608" : 1,
	"CL1609" : 1,
	"MINI_SP_1606" : 1,
	"MINI_SP_1609" : 1,
	"DAX_1606" : 1.1128,
	"DAX_1609" : 1.1128,
	"FDAX1609" : 1.1128,
	"OI609" : 1,
	"ru1609" : 1,
	"SR609" : 1,
	"ni1609" : 1,
	"hc1610" : 1,
	"CF609" : 1,
	"a1609" : 1,
	"m1609" : 1,
	"rb1610" : 1,
	"cu1608" : 1,
	"sn1609" : 1,
	"au1612" : 1,
	"v1609" : 1,
	"pp1609" : 1,
	"i1609" : 1,
	"GC1608" : 1
}

commission_factor = {
	"FDAX_DEC_16" : 1.1128,
	"FDAX_JUN_16" : 1.1128,
	"FDAX_SEP_16" : 1.1128,
	"HSIJ16" : 0.1286,
	"HSIK16" : 0.1286,
	"HSIM16" : 0.1286,
	"HSIN16" : 0.1286,
	"HSIU16" : 0.1286,
	"HSI1607" : 0.1286,
	"CL_1607" : 1,
	"CL_1608" : 1,
	"CL1608" : 1,
	"CL1609" : 1,
	"MINI_SP_1606" : 1,
	"MINI_SP_1609" : 1,
	"DAX_1606" : 1.1128,
	"DAX_1609" : 1.1128,
	"FDAX1609" : 1.1128,
	"OI609" : 1,
	"ru1609" : 1,
	"SR609" : 1,
	"ni1609" : 1,
	"hc1610" : 1,
	"CF609" : 1,
	"a1609" : 1,
	"m1609" : 1,
	"rb1610" : 1,
	"cu1608" : 1,
	"sn1609" : 1,
	"au1612" : 1,
	"v1609" : 1,
	"pp1609" : 1,
	"i1609" : 1,
	"GC1608" : 1
}

TICK_FACTOR = 0

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

	def get_num(this, contract, dir):
		if contract not in this.contracts:
			return 0

		num = 0
		list_pos = this.contracts[contract][dir]
		for pos in list_pos:
			num += pos.number

		return num

	def open(this, datetime, contract, dir, number, price, commission):
		if contract not in this.contracts: 
			this.contracts[contract] = {}
			this.contracts[contract][DIR_BUY] = []
			this.contracts[contract][DIR_SELL] = []

		if dir == DIR_BUY:
			price += TICK_FACTOR * price_tick_set[contract]
		elif dir == DIR_SELL:
			price -= TICK_FACTOR * price_tick_set[contract]

		this.contracts[contract][dir].append(Position(contract, datetime, dir, number, price))

		if contract not in this.total_profit:
			this.total_profit[contract] = 0
			this.total_commission[contract] = 30 * commission_factor[contract]
		else:
			this.total_commission[contract] += 30 * commission_factor[contract]

	def close(this, datetime, contract, dir, number, price, commission, today):
		if contract not in this.contracts:
			err = 'close error, not match contract[%s] date[%s] dir[%s] number[%s] price[%.2f]' %  (contract, datetime, dir, number, price)
			raise Exception(err)
			return
		date = datetime/1000000

		if dir == DIR_BUY:
			price += TICK_FACTOR * price_tick_set[contract]
		elif dir == DIR_SELL:
			price -= TICK_FACTOR * price_tick_set[contract]

		if contract not in this.date_profit: this.date_profit[contract] = {}
		if date not in this.date_profit[contract]: this.date_profit[contract][date] = 0
		total_profit_1 = 0
		total_sell = number
		positions = this.contracts[contract][1-dir]
		index = 0
		this_profit = 0
		while True:
			if len(positions) == 0: break
			pos = positions[index]

			# print contract, datetime
			if today and pos.datetime/1000000 != datetime/1000000: # 如果是平今，但是该仓非今仓
				loop_count = 0
				while True:
					index += 1
					loop_count += 1
					pos = positions[index]
					if pos.datetime/1000000 == datetime/1000000: break
					if loop_count > 500:
						err = 'close error, cant find close today position [%s] date[%s] dir[%s] number[%s] price[%.2f]' %  (contract, datetime, dir, number, price)
						raise Exception(err)

			remove_number = min(pos.number, total_sell)
			profit = 0
			if dir == DIR_SELL:
				profit += remove_number * (price - pos.price) * mutil_set[contract] * multi_factor[contract]
			else:
				profit += remove_number * (pos.price - price) * mutil_set[contract] * multi_factor[contract]
			total_profit_1 += profit

			this_profit += profit
						
			total_sell -= remove_number
			pos.number -= remove_number

			if pos.number == 0: positions.remove(pos)			
			if total_sell == 0: break

		this.total_profit[contract] += this_profit
		this.date_profit[contract][date] += this_profit

		if total_sell > 0: 
			err ='close error, not match contract[%s] date[%s] dir[%s] number[%s] price[%.2f]' %  (contract, datetime, dir, number, price)
			raise Exception(err)
			return
		# 手续费累加
		this.total_commission[contract] += 0 * commission_factor[contract]

		return this_profit
	
	def get_profit(this, contract):
		if not this.total_profit.has_key(contract): raise Exception('must trade before get_profit')
		return this.total_profit[contract]

	def get_commission(this, contract):
		if not this.total_commission.has_key(contract): raise Exception('must trade before get_commission')
		return this.total_commission[contract]

	def get_position_profit(this, date, query_price_func):
		profits = {}
		for contract, dir_positions in this.contracts.items():			
			#if len(dir_positions[DIR_BUY]) == 0 and len(dir_positions[DIR_SELL]) == 0: continue
			if contract not in profits: profits[contract] = 0

				# print "position price %s %.2f -  %.2f %.2f" % (date, price, buy_position_price, sel_position_price)
				# if this.date_profit.has_key(contract) and this.date_profit[contract].has_key(date):
				# 	print "dateprofit %d %.2f" % (date, this.date_profit[contract][date])
			profits[contract] += this.total_profit[contract] - this.total_commission[contract]
			
		return profits
