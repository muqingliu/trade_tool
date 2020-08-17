------------------------------------------------------------
-- 按 InstrumentID 字段作为文件名，导出其所对应的该表的所有的记录
-- db_table_name  指定的表
-- output_floder 输出的文件名字
-- 【提醒】 安全工具， 不会影响到数据库数据
------------------------------------------------------------
package.cpath = "D:\\Program Files\\Lua\\5.1\\clibs\\?.dll;" .. package.cpath
require "luasql.mysql"
require "tools"

local db_host = "www.5656k.com"
local db_user = "stock"
local db_pwd  = "8i9op0Z"
local db_dbase= "stock"
local db_port= 3306

local db_table_name = "hq_shfe_k1"    -- 表名
local output_floder = "导出" .. db_table_name .. "表数据"  -- 输出文件夹名称

-----------------------------------------------------------------------------------------
--               以下代码在不清楚的情况下，请不要随意修改
-----------------------------------------------------------------------------------------

function main()
	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))
	
	local sqlStatement
	local tFileName = {}   -- 保存文件名
	-- 获取 InstrumentID 的字段名字
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
	
	-- 写文件
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


