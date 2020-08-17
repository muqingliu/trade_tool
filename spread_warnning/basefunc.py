from common import db


# 交易日期类型
TRADE_DATE_TYPE = define.enum(month = 0, quarter = 1, halfyear =2 )

db_info = {
	'host' 		: '192.168.1.101',
    # 'host' 		: 'localhost',
	'user' 		: 'root',
	# 'password' 	: 'w1c4h7',
    'password' 	: '1',
	'db' 		: 'stock_data',
    # 'port'      : 3306,
    'port'      : 13306,
    'charset'   :   'utf8'
}

def create_database(info=None):
    if info == None: info = db_info
    return db.DB(host=info['host'],user=info['user'], passwd=info['password'], db=info['db'], charset= info['charset'], port=info['port'])
