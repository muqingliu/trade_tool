import os
import log
import db
import scanf
import ConfigParser

class SystemConfig(object):
    # 配置文件信息结构
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.name = ini_parser.get("main", "name")
        self.profit_dir = ini_parser.get("main", "profit_dir")

        self.db_user = ini_parser.get("db", "user")
        self.db_password = ini_parser.get("db", "password")
        self.db_host = ini_parser.get("db", "host")
        self.db_database = ini_parser.get("db", "database")
        self.db_table = ini_parser.get("db", "table")
        self.db_charset = ini_parser.get("db", "charset")
        self.db_port = ini_parser.getint("db", "port")

if __name__ == '__main__':
	print("running...")

	system_info = SystemConfig("system.ini")

	# db_execute = db.DB(system_info.db_host, system_info.db_user, system_info.db_password, system_info.db_database, system_info.db_table, 
	# 		   		   system_info.db_charset, system_info.db_port)

	fp_sql = open("trade_records.sql", "wb")

	#运行和写入删除语句
	del_sql = "delete from %s where tradeName='%s' && (contract='ru' || contract = 'rb');" % (system_info.db_table, system_info.name)
	#db_execute.Execute(del_sql)
	fp_sql.write(del_sql)
	fp_sql.write("\n")

	for root, dirs, files in os.walk(system_info.profit_dir):
		for name in files:
			index = name.rfind("_")
			contract = name[0:index]

			path = os.path.join(root, name)

			fp_profit = open(path, "rb")
			print path
			line = fp_profit.readline()

			sysID = 1
			while(len(line) > 0):
				# print line
				profit = scanf.sscanf(line, "%d %d %f %f %f %f %d")

				dir_str = "买入" if profit[1] == 0 else "卖出"
				sql = "insert into %s values('%s','%s','',%d, '开',%u,%u,'%s',%f,%f,%f,%f,%u);" % (system_info.db_table,
					  system_info.name, contract, sysID, profit[0]/10000,profit[0]%10000*100,dir_str,profit[2],profit[3],profit[4],profit[5],
					  profit[6])
				if profit[3] != 0:
					sql = "insert into %s values('%s','%s','',%d, '平',%u,%u,'%s',%f,%f,%f,%f,%u);" % (system_info.db_table,
					  	  system_info.name, contract, sysID, profit[0]/10000,profit[0]%10000*100,dir_str,profit[2],profit[3],profit[4],profit[5],
						  profit[6])

				# db_execute.Execute(sql)
				fp_sql.write(sql)
				fp_sql.write("\n")

				line = fp_profit.readline()
				sysID += 1

			fp_profit.close()

	fp_sql.close()