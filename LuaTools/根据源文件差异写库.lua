------------------------------------------------------------
-- 根据源文件数据同数据库数据对比，根据源文件进行差异补库
-- INSERT_FILE 保存需要检查的源文件，如果为空，则获取当前文件下的所有.txt文件作为源文件
-- output_floder 输出文件夹
-- 输出文件夹里的 '未识别的文件.txt' 意味着商品在config.lua中未被配置
-- 【提醒】 改库工具， 会修改到数据库数据
------------------------------------------------------------
package.cpath = "D:\\Program Files\\Lua\\5.1\\clibs\\?.dll;" .. package.cpath
require "luasql.mysql"
require "tools"

local db_host = "localhost"
local db_user = "root"
local db_pwd  = "1"
local db_dbase= "stock"
local db_port= 3306

local INSERT_FILE = {}
local output_floder = "填补数据库数据"

-----------------------------------------------------------------------------------------
--               以下代码在不清楚的情况下，请不要随意修改
-----------------------------------------------------------------------------------------

-- 插入库操作
function insertDB(con, tDiff, tUnFile)
	os.execute("mkdir " .. output_floder)
	if not isEmpty(tDiff) then
		for bourse, v in pairs(tDiff) do  -- 获得交易所
			os.execute("md " .. output_floder .. "\\" .. bourse)
			local strValue = ""
			local sql = "INSERT INTO " .. bourse .. " (InstrumentID,Time,OpenPrice,HighestPrice,LowestPrice,ClosePrice,Volume) VALUES "
			for ins,t in pairs(v) do   -- 获得订单
				if not isEmpty(t) then
					local f = io.open(output_floder .. "/" .. bourse .. "/" .. ins .. ".txt", "w")
					for _, vv in ipairs(t) do    -- 获得记录
						strValue = sql ..  "('" .. vv.InstrumentID .. "'," .. vv.Time .. "," .. vv.OpenPrice .. ","
						.. vv.HighestPrice .. "," .. vv.LowestPrice .. "," .. vv.ClosePrice .. "," .. vv.Volume .. ");"
						f:write(dbRow2srcRow(vv) .. "\n")
						con:execute(strValue)
					end
					f:close()
				end
			end
		end
	else
		print("没有需要写入数据库的数据")
	end	
	
	if #tUnFile > 0 then
		local f = assert(io.open(output_floder .. "/" .. "未识别的文件.txt", "w"))
		for k,v in ipairs(tUnFile) do
			f:write(v .. "\n")
		end
		f:close()
	end
end

function main()
	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))
	if #INSERT_FILE == 0 then
		INSERT_FILE = getCurDirAllTxt()
	end
	local tDiff = {} -- 保存写入库中的数据 k-str-交易所 v-table-记录
	local tUnFile={} -- 保证不知道放在那张表的数据源文件
	for _, filepath in pairs(INSERT_FILE) do
		print("---------->" .. filepath)
		local bourse = getBourseBysrcFile(filepath) -- 获取交易所
		if not bourse then 
			table.insert(tUnFile, filepath)
		else
			local ins = getFileNameByPath(filepath)
			-- 库中读取数据
			local cur = con:execute(string.format([[
				SELECT InstrumentID,Time,OpenPrice,HighestPrice,LowestPrice,ClosePrice,Volume 
				FROM %s
				WHERE InstrumentID = '%s';
			]],bourse,ins))
			local tDBInfo = {}   -- 保存源数据内容 k Time,v {}
			while true do
				local t = cur:fetch({}, "a")
				if not t then break end
				tDBInfo[t.Time] = t
			end
			cur:close()
			-- 源文件中读取数据
			local tSrcInfo = {}  -- 源文件数据内容 k Time,v {}
			local f = assert(io.open(filepath,"r"), "not find file ".. filepath)
			while true do
				local l = f:read()
				if not l then
					break
				end
				local t = srcRow2dbRow(l)
				if t then
					t.InstrumentID = ins
					tSrcInfo[t.Time] = t
				end
			end
			f:close()
			-- 比较差异写库
			if not tDiff[bourse] then
				tDiff[bourse] = {}
			end
			if not tDiff[bourse][ins] then
				tDiff[bourse][ins] = {}
			end
			local tInsert = {}
			for k,v in pairsByKey(tSrcInfo) do
				if not tDBInfo[k] then
					table.insert(tInsert, v)
				end
			end
			tDiff[bourse][ins]= tInsert
			print("finish " .. ins)
		end
	end
	
	insertDB(con,tDiff,tUnFile)
	
	con:close()
	env:close()
end

main()
