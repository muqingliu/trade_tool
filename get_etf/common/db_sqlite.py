from __future__ import unicode_literals
import sqlite3
import shutil
import file_op
import func
import time
import log
import os
from manga import *
import sites_mgr

#----------------------
def manga_db2dic(manga_db):

	mng = dict(
		ID = manga_db[0],
		name = manga_db[1], 
		info_url = manga_db[2], 
		author = manga_db[3], 
		type = manga_db[4], 
		genre = manga_db[5], 
		status = manga_db[7],
		detail = manga_db[6]
		)

	return mng

#----------------------
class DB(object):
	conn = {'db_name':[0, None]}
	site_name = None

	def BeginSave(this):
		this.db.execute("BEGIN TRANSACTION")

	def EndSave(this):
		this.db.execute("COMMIT TRANSACTION")

	def Commit(this):
		this.GetConn().commit()

	def Execute(this, sql, *the_tuple):
		this.db.execute(sql, the_tuple)
		this.Commit()

	def Query(this, sql, *the_tuple):
		this.db.execute(sql, the_tuple)

	def TableExist(this, name):
		this.Query("SELECT count(0) FROM [sqlite_master] WHERE [name] = ?", name)
		return this.FetchOne()[0] >= 1
	
	def HasTable(this):
		return this.TableExist(this.table_name)

	def Refresh(this):
		this.Query('SELECT count(0) FROM [%s]' % this.table_name)
		this.FetchOne()

	# row object
	def FetchOne(this):
		return this.db.fetchone()
	
	def FetchOne_1_Col(this):
		row = this.FetchOne()
		if not row : return None
		return row[0]

	#list of row object
	def FetchAll(this):
		return this.db.fetchall()

	def Open(this, db_name, table_name, site_name):
		this.db_name = db_name
		this.table_name = table_name
		this.site_name = site_name

		if not this.GetConn():
			conn = sqlite3.connect(db_name)
			conn.row_factory = sqlite3.Row
			conn.text_factory = str
			this.SetConn(conn)

		this.db = this.GetConn().cursor()

	def LastID(this):
		return this.db.lastrowid

	def GetConn(this):
		if this.db_name in DB.conn:
			return DB.conn[this.db_name]
		return None

	def SetConn(this, conn):
		DB.conn[this.db_name] = conn

	def __del__(this):
		#conn = this.GetConn()
		#if not conn : return
		#conn.close()
		#this.SetConn(None)
		pass # 暂时不做清理

#----------------------
# update recorde
# 只读可以不填 site_name
class UDB(DB):
	def __init__(this, site_name, test = False):
		db_test_fix = ''
		if test : db_test_fix = '_TST'
		this.Open('../Update%s.db' % db_test_fix, 'UPDT', site_name)
		this.CreateTable()

	def CreateTable(this):
		if this.HasTable() :return;
		sql = 'CREATE TABLE [UPDT] (\
			"GID" INTEGER NOT NULL ,\
			"site" TEXT NOT NULL ,\
			"MID" INTEGER NOT NULL ,\
			"CID" INTEGER NOT NULL ,\
			"dt" DATETIME NOT NULL\
			)'

		this.Execute(sql)

	def AddUpdate(this, GID, mid, cid):
		#the time is the seconds from epoch(1970.1.1.0.0.0) in UTC
		#using  time.localtime(xxx) to get local time or,
		#time.gmtime(xxx) to get the UTC time.
		date = int(time.time())

		sql = 'INSERT INTO [UPDT] ("GID","site","MID","CID","dt") VALUES (?,?,?,?,?)'
		this.Execute(sql, GID, this.site_name, mid, cid, date)

	def GetLastUpdate(this, GID):
		this.Query('SELECT [site], [CID], [dt] FROM UPDT WHERE GID = ? ORDER BY [dt] DESC LIMIT 1', GID)
		return this.FetchOne()

#----------------------
# Popular DB
class PDB(DB):
	def __init__(this):
		this.Open('../Pop.db', 'POP', '')
		this.CreateTable()

	def CreateTable(this):
		if this.HasTable() :return;
		sql = 'CREATE TABLE [POP] (\
			"GID" INTEGER PRIMARY KEY NOT NULL UNIQUE,\
			"cnt" INTEGER NOT NULL \
			)'

		this.Execute(sql)

	def AddCount(this, gid, cnt = 1):
		if this.NotHaveGID(gid):
			this.Execute('INSERT INTO POP ("GID","cnt") VALUES (?, ?)', gid, cnt)
			return

		sql = 'UPDATE [POP] set [cnt] = [cnt] + ? WHERE GID = ?'
		this.Execute(sql, cnt, gid)

	def GetCount(this, gid):
		if this.NotHaveGID(gid): return 0
		this.Query('SELECT cnt FROM [POP] WHERE [GID] == ?', gid)
		return this.FetchOne_1_Col()

	def NotHaveGID(this, gid):
		this.Query('SELECT COUNT(0) FROM [POP] WHERE [GID] == ?', gid)
		return this.FetchOne_1_Col() == 0

	def Erase(this, gid):
		if this.NotHaveGID(gid): return
		sql = 'delete from POP where GID == ?'
		this.Execute(sql, gid)

#----------------------
# chapters DB
class CDB(DB):
	def __init__(this, gid, site_name, test = False):
		db_test_fix = ''
		if test : db_test_fix = '_TST'
		mdb_path = file_op.get_book_dir(gid, file='m%s.db'%db_test_fix)

		this.Open(mdb_path, 'CHPT_%s'%site_name, site_name)
		this.CreateTable()

	def CreateTable(this):
		if this.HasTable() :return;
		sql = 'CREATE TABLE [%s] ("ID" INTEGER PRIMARY KEY NOT NULL UNIQUE, \
			"name" TEXT, "url" TEXT, "fetched" INTEGER DEFAULT (0), \
			"tstamp" INTEGER DEFAULT (0))' % this.table_name
		this.Execute(sql)

	def Has(this, cid):
		this.Query('SELECT COUNT(0) FROM [%s] WHERE [ID] == ?' % this.table_name, cid)
		return this.FetchOne_1_Col() >= 1

	def Save(this, cid, cname, curl, ctime):
		if this.Has(cid) : return
		this.Execute('INSERT INTO [%s]([ID], [name], [url], [tstamp]) VALUES (?, ?, ?, ?)' % this.table_name, 
			cid, cname, curl, ctime)

	def Get(this, cid):
		if not this.Has(cid) : return None
		this.Query('SELECT [ID],[name],[url],[tstamp] FROM [%s] WHERE [ID] = ?' % this.table_name, cid)
		return this.FetchOne()

	def GetChaptersCount(this):
		this.Query('SELECT COUNT(0) FROM [%s]' % this.table_name)
		return this.FetchOne_1_Col()

	def UpdateChapterFetched(this, cid, num):
		this.Execute("UPDATE [%s] SET [fetched] = ?, [url]= NULL WHERE ID = ?" % this.table_name, num, cid)

	def GetAllChpatersFetched(this):
		this.Query('SELECT [ID], [name], [url], [fetched], [tstamp]  FROM [%s] WHERE [fetched] > 0' % this.table_name)
		return this.FetchAll()

#----------------------
# Mangas DB
class MDB(DB):

	def __init__(this, site_name, test=False):
		db_test_fix = ''
		if test : db_test_fix = '_TST'

		this.Open('../MangoInfo%s.db' % db_test_fix, 'ENTR_%s'%site_name, site_name)
		this.CreateTable()

	def CreateTable(this):
		if this.HasTable() :return		
		sql = 'CREATE TABLE [%s] ("ID" INTEGER PRIMARY KEY NOT NULL UNIQUE, \
		"name" TEXT, "info_url" TEXT, "author" TEXT, "type" TEXT, "genre" TEXT \
		, "detail" TEXT, "status" TEXT)' % this.table_name
		this.Execute(sql)

	def GetGID(this, name):
		if isinstance(name, dict) : name = name['name']
		this.Query('SELECT [ID] FROM [%s] where [name] == ?' % this.table_name, name)
		iId = this.FetchOne_1_Col()
		if not iId : return 0
		return iId

	def Save(this, m):
		name = m['name']
		if this.GetGID(name) == 0: return
		sql = "INSERT INTO [%s]([name],[info_url],[author],[type],[genre],[detail],[status]) \
			VALUES (?, ?, ?, ?, ?, ?, ?)" % this.table_name
		this.Execute(sql, name, m['info_url'], m['author'], m['type'], 
			m['genre'], m['detail'], m['status'])
		return this.LastID()
	
	def UpdateStatus(this, mid, st):
		sql = "UPDATE [%s] SET [status] = ? WHERE [ID] = ?" % this.table_name
		this.Execute(sql, st, mid)

	def Get(this, mid):
		sql = "SELECT * FROM [%s] WHERE ID == ?" % this.table_name
		result = this.Query(sql, mid);
		row = this.FetchOne()

		if not row : return None
		ma =  manga_db2dic(row)
		ma['ID'] = mid
		ma['site'] = this.site_name
		return ma

	def Seal(this, ID):
		sql = "UPDATE [%s] SET [status] = 'X' WHERE [ID] = ?" % this.table_name
		this.Execute(sql, ID)

	def UpdateDesc(this, ID, desc):
		sql = "UPDATE [%s] SET [detail] = ? WHERE [ID] = ?" % this.table_name
		this.Execute(sql, desc, ID)

	def Count(this):
		this.Query("SELECT COUNT(0) FROM [%s]" % this.table_name)
		return this.FetchOne()[0]

#----------------------
# GlobalID DB
class GDB(DB):

	def __init__(this, site_name, test = False):
		db_test_fix = ''
		if test : db_test_fix = '_TST'
		this.Open('../GlobalID%s.db' % db_test_fix, 'ID_MATCH', site_name)
		this._CreateTableIfNot()

	def _CreateTableIfNot(this):
		if not this.TableExist('ID_MATCH') :
			this.Execute('CREATE TABLE [ID_MATCH] ("GID" INTEGER PRIMARY KEY NOT NULL UNIQUE)')

		this.Execute('INSERT OR IGNORE INTO [ID_MATCH]([GID]) VALUES(0)')
		this.CrateColumn()

	def _HasColumn(this):
		this.Query("select [sql] from sqlite_master where [name] = 'ID_MATCH'")
		strg = this.FetchOne_1_Col()
		pos = strg.find('ID_%s' % this.site_name)
		if pos >= 0 : return True
		return False

	def CrateColumn(this):
		if not this.site_name : return
		if not this._HasColumn() :
			sql = 'ALTER TABLE [ID_MATCH] ADD COLUMN [ID_%s] INTEGER' % this.site_name
			this.Execute(sql)
		#record the entries db name
		this.Execute("UPDATE [ID_MATCH] SET [ID_%s]= ? WHERE GID == 0" % this.site_name, this.site_name)

	def AddToNewGlobalID(this, mid, base=0):
		if not this.site_name : return
		gid = this.GetGID(mid)
		# alreaady exist
		if gid > 0 : return gid

		sql = 'INSERT INTO [ID_MATCH]([ID_%s]) VALUES(?)' % this.site_name
		#log.WriteDetail(sql)
		this.Execute(sql, mid)
		gid = this.LastID()

		if (base != 0) and (gid < base):
			new_gid = gid + base
			this.Execute('UPDATE [ID_MATCH] SET GID = %d WHERE GID == ?' % new_gid, gid)
			gid = new_gid
		return gid

	def AddToGlobalID(this, mid, GID):
		if not this.site_name : return
		# TODO: 如果mid已经存在，换位子
		this.Execute("UPDATE [ID_MATCH] SET [ID_%s]= ? WHERE GID == ?" % this.site_name, mid, GID)

	def GetGID(this, mid):
		if not this.site_name : return
		this.Query("SELECT count(0), [GID] FROM [ID_MATCH] WHERE [ID_%s] == ?" % this.site_name, mid)
		row = this.FetchOne()
		if  row[0] == 0 : return 0
		return row[1]

	def GetMID(this, GID):
		this.Query("SELECT count(0), [ID_%s] FROM [ID_MATCH] WHERE [GID] == ?" % this.site_name, GID)
		row = this.FetchOne()
		if  row[0] == 0 : return 0
		return row[1]

	def site_names_list(this):
		this.Query("SELECT * FROM [ID_MATCH] WHERE [GID] == 0")
		row = this.FetchOne()
		if not row : return None
		return [name for name in row]

#----------------------
# for looping only
class GDB_T(GDB):
	def __init__(this, test=False):
		db_test_fix = ''
		if test : db_test_fix = '_TST'
		gdb = GDB('', test) # make sure the db is existing
		shutil.copyfile(gdb.db_name, '../GlobalID_TMP.db')
		this.Open('../GlobalID_TMP.db', 'ID_MATCH', '')

#----------------------
# TESTED
def get_mng_by_gid(gid, test=False):
	mng = {}
	gdb = GDB('', test)
	site_list = gdb.site_names_list()

	if not site_list : return mng
	for site_name in site_list[1:]:
		gdb.site_name = site_name
		mid = gdb.GetMID(gid)
		if not mid : continue
		mdb = MDB(site_name, test)
		mng = mdb.Get(mid)
		mng['GID'] = gid
		return mng

	return mng
#----------------------

# 遍历 DB.
# call_back(row) return True 为继续，否则为停止遍历
# 随便测试下，6000条是最优方案

def iterate_DB(call_back, adb, condition='', user_data=None, rows_once=6000, limit=0):
	#iterate all rows of db:
	adb.Query("SELECT COUNT(0) FROM [%s] %s" % (adb.table_name, condition))
	cnt = adb.FetchOne_1_Col()

	if limit :
		cnt = min(cnt, limit)
		rows_once = cnt

	if cnt < rows_once : 
		rows_once = cnt

	for offset in func.range_step(0, cnt, rows_once):
		result = adb.Query("SELECT * FROM [%s] %s LIMIT ? OFFSET ?" % (
			adb.table_name, condition),
			rows_once, offset)
		
		row = adb.FetchOne()
		while(row):
			if user_data:
				if not call_back(row, user_data):return
			else:
				if not call_back(row):return

			row = adb.FetchOne()

	#这个函数可以避免不必要的 database locked.原因不明
	adb.Refresh()

#----------------------
# 遍历 MDB
# call_back() return True to continue
def iterate_MDB_entries(call_back, site, rows = 6000):
	adb = site.get_MDB()
	iterate_DB(call_back, adb, rows_once = rows)

#----------------------
# 遍历所有漫画

def iterate_Mangas(func_each_site_mng):
	idb = GDB_T()
	iterate_DB(__loop_over_each_gdb_entry, idb, 'WHERE GID > 0', func_each_site_mng)


mdb = MDB('BG')
#----------------------
# TESTED
def __loop_over_each_gdb_entry(id_row, func):
	#[GID,	BG,	KKD,	XXX]
	#[1,	2,	4,		None]
	#[2,	3,	None,	None]

	GID = id_row[0]
	mid = id_row[1]

	print "get manga id %d" % mid
	mng = mdb.Get(mid)

	mng['GID'] = GID
	ret = func(mng)

	if ret == 'NEXT_GID': return True

	return False

