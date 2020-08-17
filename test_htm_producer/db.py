
import MySQLdb
import func
import log

class DB(object):

	cursor = None
	conn = None
	table_name = None

	def __init__(this, host, user, passwd, db, table_name='', port=3306):		
		try:
			this.conn = MySQLdb.connect(host, user, passwd, db, port)
			this.cursor = this.conn.cursor()
			this.table_name = table_name
		except :
			log.WriteError ('Error: cant connect db names %s from host %s' % (db, host) )
		    
	def IsConnect(this):
		return this.conn != None

	def Query(this, sql, *the_tuple):
		this.cursor.execute(sql % the_tuple)

	def Execute(this, sql, *the_tuple):
		if the_tuple:
			return this.cursor.execute(sql % the_tuple)
		else:
			return this.cursor.execute(sql)
		#this.Commit()

	# row object
	def FetchOne(this):
		return this.cursor.fetchone()
	
	def FetchOne_1_Col(this):
		return this.FetchOne()[0]

	#list of row object
	def FetchAll(this):
		return this.cursor.fetchall()

	def __del__(this):
		if this.conn:			
			this.cursor.close()
			this.conn.close()


def iterate_DB(call_back, adb, condition='', user_data=None, rows_once=6000, limit=0):
	#iterate all rows of db:
	if not adb or not adb.IsConnect(): return

	sql = 'SELECT COUNT(0) FROM %s %s' % (adb.table_name, condition)
	adb.Query(sql)
	cnt = adb.FetchOne_1_Col()

	if limit :
		cnt = min(cnt, limit)
		rows_once = cnt

	if cnt < rows_once : 
		rows_once = cnt

	for offset in func.range_step(0, cnt, rows_once):
		sql = 'SELECT * FROM %s %s LIMIT %u OFFSET %u' % (adb.table_name, condition, rows_once, offset)
		result = adb.Query(sql)
		
		row = adb.FetchOne()
		while(row):
			if user_data:
				if not call_back(row, user_data):return
			else:
				if not call_back(row):return

			row = adb.FetchOne()
