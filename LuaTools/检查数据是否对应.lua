------------------------------------------------------------
-- ���������InstrumentID�Ƿ����ڶ�Ӧ�Ľ�����
-- ͨ���� 'config.lua' �е� cfgBourse �������ã����û������Щ��������
-- ���� ����ļ��� ��ʾ ��none����ʱӦ�ý����������õ� 
-- �����ѡ� ��ȫ���ߣ� ����Ӱ�쵽���ݿ�����
------------------------------------------------------------
package.cpath = "D:\\Program Files\\Lua\\5.1\\clibs\\?.dll;" .. package.cpath
require "luasql.mysql"
require "tools"

local db_host = "localhost"
local db_user = "root"
local db_pwd  = "1"
local db_dbase= "stock"
local db_port= 3306

local db_table_name = "hq_dce_k1"
local output_floder = db_table_name .. "���Ʒ��Ӧ���.txt"

-----------------------------------------------------------------------------------------
--               ���´����ڲ����������£��벻Ҫ�����޸�
-----------------------------------------------------------------------------------------

function printReport(t)
	local f = assert(io.open(output_floder, "w"))
	for k, v in pairs(t) do
		f:write("************************************************\n")
		f:write("�����ñ��л�Ϥ�����ڱ�" .. k .. "������InstrumentID��\n")
		f:write("************************************************\n")
		local leng = 0
		for kk, vv in pairs(v) do
			f:write(vv.ins .. "\t")
			leng = leng + 1
			if leng % 6 == 0 then
				f:write("\n")
			end
		end
		f:write("\n================================================\n\n\n")
	end
	f:close()
end

function main()
	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))
	local tInfo = {}  -- k ������v {} -- {ins} 
	local filter = {}
	
	local sqlStatement = string.format([[
		SELECT DISTINCT InstrumentID
		FROM %s;
	]],db_table_name)
	local cur = con:execute(sqlStatement)
	while true do
		local t = cur:fetch({}, "a")
		if not t then
			break
		end
		local flag = string.match(t.InstrumentID, "(%a+)")
		local bourse = getBourseBysrcFile(t.InstrumentID)
		bourse = bourse and bourse or "none"
		local temp = {ins=flag}
		if not tInfo[bourse] then
			tInfo[bourse] = {}			
		end
		if not filter[flag] then
			table.insert(tInfo[bourse], temp)
			filter[flag] = true
		end
	end
	
	printReport(tInfo)
	
	cur:close()
	con:close()
	env:close()
end

main()