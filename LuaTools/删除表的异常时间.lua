------------------------------------------------------------
-- ɾ������쳣ʱ��
-- ��ͨ�� ִ�� '���ָ��������������.lua' �ļ�������������ļ��и�Ŀ¼�£��ҵ� '�쳣ʱ���.txt'
-- �����ļ����ñ��ļ�ͬ��Ŀ¼�£�Ȼ�����б���
-- ���ȡ'�쳣ʱ���.txt'��һ����Ϊ������ Ȼ��ɾ����Щʱ���Ӧ�������ֶ�
-- ��ע�⡿ ��ִ�б��ļ�����ȼ���� '�쳣ʱ���.txt' �����ʱ��
-- �����ѡ� �Ŀ⹤�ߣ� ���޸ĵ����ݿ�����
------------------------------------------------------------
package.cpath = "D:\\Program Files\\Lua\\5.1\\clibs\\?.dll;" .. package.cpath
require "luasql.mysql"

local db_host = "localhost"
local db_user = "root"
local db_pwd  = "1"
local db_dbase= "stock"
local db_port= 3306

-----------------------------------------------------------------------------------------
--               ���´����ڲ����������£��벻Ҫ�����޸�
-----------------------------------------------------------------------------------------

function main()
	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))
	local db_table_name = ""
	local tExpAll = {} -- �����쳣ʱ��ı�  -- k num, v {a,b}
	
	-- ��ȡ�쳣ʱ��
	local f = io.open("�쳣ʱ���.txt", "r")
	if f then
		db_table_name = f:read()
		local str = ""
		local a,b
		while true do
			str = f:read()
			if not str then break end
			a,b = string.match(str, "(%S+)%s+(%S+)")
			table.insert(tExpAll, {a,b})
		end
		f:close()
	end
	
	-- ɾ���쳣ʱ��
	local tFileName = {}   -- �����ļ���
	local sqlStatement = ""
	for _, v in ipairs(tExpAll) do
		sqlStatement = string.format([[
			DELETE
			FROM %s
			WHERE Time = %d AND InstrumentID = '%s';
		]],db_table_name, v[2], v[1])	
		print(sqlStatement)
		assert(con:execute(sqlStatement))
	end
	
	con:close()
	env:close()
end

main()
