------------------------------------------------------------
-- �� InstrumentID �ֶ���Ϊ�ļ���������������Ӧ�ĸñ�����еļ�¼
-- db_table_name  ָ���ı�
-- output_floder ������ļ�����
-- �����ѡ� ��ȫ���ߣ� ����Ӱ�쵽���ݿ�����
------------------------------------------------------------
package.cpath = "D:\\Program Files\\Lua\\5.1\\clibs\\?.dll;" .. package.cpath
require "luasql.mysql"
require "tools"

local db_host = "www.5656k.com"
local db_user = "stock"
local db_pwd  = "8i9op0Z"
local db_dbase= "stock"
local db_port= 3306

local db_table_name = "hq_shfe_k1"    -- ����
local output_floder = "����" .. db_table_name .. "������"  -- ����ļ�������

-----------------------------------------------------------------------------------------
--               ���´����ڲ����������£��벻Ҫ�����޸�
-----------------------------------------------------------------------------------------

function main()
	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))
	
	local sqlStatement
	local tFileName = {}   -- �����ļ���
	-- ��ȡ InstrumentID ���ֶ�����
	sqlStatement = string.format([[
		SELECT DISTINCT InstrumentID AS FileName
		FROM %s WHERE InstrumentID = 'rb1501';
	]],db_table_name)
	local cur = assert(con:execute(sqlStatement))
	while true do
		local t = cur:fetch({}, "a")
		if not t then break end
		tFileName[t.FileName] = true
	end
	
	-- д�ļ�
	if not getCurDirAll()(output_floder) then
		os.execute("mkdir " .. output_floder)
	end
	for k,_ in pairs(tFileName) do
		local f = io.open(output_floder .. "/" ..k .. ".txt", "w")
		if f then
			sqlStatement = string.format([[
				SELECT Time,OpenPrice,HighestPrice,LowestPrice,ClosePrice,Volume 
				FROM %s 
				WHERE InstrumentID = '%s'
				ORDER BY Time;
				]], db_table_name, k)
			local curTemp = assert(con:execute(sqlStatement))
			while true do
				local t = curTemp:fetch({}, "a")
				if not t then break end
				f:write(dbRow2srcRow(t) .. "\n")
			end
			curTemp:close()
			f:close()
			print("output " .. k)
		end
	end

	cur:close()
	con:close()
	env:close()
	
end

main()


