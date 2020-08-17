------------------------------------------------------------
-- 检查所属的InstrumentID是否属于对应的交易所
-- 通过在 'config.lua' 中的 cfgBourse 表中配置，如果没有在这些表中配置
-- 则在 输出文件中 显示 表none，此时应该将该类型配置到 
-- 【提醒】 安全工具， 不会影响到数据库数据
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
local output_floder = db_table_name .. "表产品对应情况.txt"

-----------------------------------------------------------------------------------------
--               以下代码在不清楚的情况下，请不要随意修改
-----------------------------------------------------------------------------------------

function printReport(t)
	local f = assert(io.open(output_floder, "w"))
	for k, v in pairs(t) do
		f:write("************************************************\n")
		f:write("从配置表中获悉，属于表" .. k .. "有以下InstrumentID：\n")
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
	local tInfo = {}  -- k 表名；v {} -- {ins} 
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