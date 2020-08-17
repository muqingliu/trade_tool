------------------------------------------------------------
-- ɾ��ָ�����е��ظ���ʱ��
-- ��InstrumentIDһ��������£�������ͬ��ʱ�䣬ID�Ƚϴ�Ľ���ɾ��
-- db_table_name ָ���ı���
-- folder_name ɾ����ɺ󣬻�������ļ�������ɾ����������
-- �����ѡ� �Ŀ⹤�ߣ� ���޸ĵ����ݿ�����
------------------------------------------------------------
package.cpath = "D:\\Program Files\\Lua\\5.1\\clibs\\?.dll;" .. package.cpath
require "luasql.mysql"

local db_host = "localhost"
local db_user = "root"
local db_pwd  = "1"
local db_dbase= "stock"
local db_port= 3306

local db_table_name = "hq_shfe_k1"
local folder_name = "ɾ��"..db_table_name.."����ֶ�"  -- ����ļ�������

-----------------------------------------------------------------------------------------
--               ���´����ڲ����������£��벻Ҫ�����޸�
-----------------------------------------------------------------------------------------

function main()
	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))
	
	-- ����Ҫɾ�����ֶΣ���ʱ������
	local tFileName = {}   -- �����ļ���
	local sqlStatement = string.format([[
		SELECT id,Time,InstrumentID
		FROM %s;
	]],db_table_name)
	local cur = assert(con:execute(sqlStatement))
	local f = assert(io.open("�ڱ�"..db_table_name.."��ɾ���ظ�ʱ��.txt", "w"))
	local sql = ""
	while true do
		local t = cur:fetch({}, "a")
		if not t then break end
		local flag = t.InstrumentID .. t.Time
		if tFileName[flag] then
			sql = string.format([[
				DELETE
				FROM %s
				WHERE id=%d;
			]],db_table_name, t.id)
			con:execute(sql)
			f:write(t.InstrumentID .. "\t" .. t.id .. "\t" .. t.Time .. "\n")
			print(t.InstrumentID, t.Time)
		else
			tFileName[flag] = true
		end
	end	
	
	cur:close()
	f:close()
	con:close()
	env:close()
end

main()
