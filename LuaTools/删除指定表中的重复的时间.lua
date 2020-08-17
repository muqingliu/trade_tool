------------------------------------------------------------
-- 删除指定表中的重复的时间
-- 在InstrumentID一样的情况下，两个相同的时间，ID比较大的将被删除
-- db_table_name 指定的表名
-- folder_name 删除完成后，会在这个文件下生成删除掉的数据
-- 【提醒】 改库工具， 会修改到数据库数据
------------------------------------------------------------
package.cpath = "D:\\Program Files\\Lua\\5.1\\clibs\\?.dll;" .. package.cpath
require "luasql.mysql"

local db_host = "localhost"
local db_user = "root"
local db_pwd  = "1"
local db_dbase= "stock"
local db_port= 3306

local db_table_name = "hq_shfe_k1"
local folder_name = "删除"..db_table_name.."表的字段"  -- 输出文件夹名称

-----------------------------------------------------------------------------------------
--               以下代码在不清楚的情况下，请不要随意修改
-----------------------------------------------------------------------------------------

function main()
	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))
	
	-- 保存要删除的字段，以时间区别
	local tFileName = {}   -- 保存文件名
	local sqlStatement = string.format([[
		SELECT id,Time,InstrumentID
		FROM %s;
	]],db_table_name)
	local cur = assert(con:execute(sqlStatement))
	local f = assert(io.open("在表"..db_table_name.."中删除重复时间.txt", "w"))
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
