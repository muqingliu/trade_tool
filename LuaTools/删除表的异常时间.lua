------------------------------------------------------------
-- 删除表的异常时间
-- 先通过 执行 '检查指定表数据完整性.lua' 文件后，在其输出的文件夹根目录下，找到 '异常时间表.txt'
-- 将该文件放置本文件同级目录下，然后运行本件
-- 会获取'异常时间表.txt'第一行作为表名， 然后删除这些时间对应的所有字段
-- 【注意】 在执行本文件最好先检查下 '异常时间表.txt' 里面的时间
-- 【提醒】 改库工具， 会修改到数据库数据
------------------------------------------------------------
package.cpath = "D:\\Program Files\\Lua\\5.1\\clibs\\?.dll;" .. package.cpath
require "luasql.mysql"

local db_host = "localhost"
local db_user = "root"
local db_pwd  = "1"
local db_dbase= "stock"
local db_port= 3306

-----------------------------------------------------------------------------------------
--               以下代码在不清楚的情况下，请不要随意修改
-----------------------------------------------------------------------------------------

function main()
	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))
	local db_table_name = ""
	local tExpAll = {} -- 保存异常时间的表  -- k num, v {a,b}
	
	-- 获取异常时间
	local f = io.open("异常时间表.txt", "r")
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
	
	-- 删除异常时间
	local tFileName = {}   -- 保存文件名
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
