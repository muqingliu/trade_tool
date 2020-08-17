------------------------------------------------------------
-- 主要检查数据库数据在指定表的时间上的延续性
-- 检查内容：1、表中所有日期的并集，扣除法定假日和周六和周日
--           2、根据交易所的交易时间，检查时间的缺漏、异常、重复的情况
-- db_table_name 指定检查的表，该表名作为交易所名称
-- folder_name 分析完成后，输出的文件目录
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

local db_table_name = "hq_shfe_k1"
local folder_name = "分析"..db_table_name.."结果"  -- 输出文件夹名称

-----------------------------------------------------------------------------------------
--               以下代码在不清楚的情况下，请不要随意修改
-----------------------------------------------------------------------------------------

-- local tradeTime = cfgTradeTime[db_table_name]
local tradeTime 
-- 打印时间分析报表
-- tRep 重复时间 k 时间 v 次数
-- tLose 缺漏的时间 k 时间 v true
-- tExp 有异常的时间 k 时间 v true
-- ret tRep次数 tLose次数 tExp次数
function printTime(fileName,tRep, tLose, tExp)
	local path = folder_name .. "/" .. fileName .. "/"
	-- 打印重复时间
	local f = io.open(path .. "重复时间.txt", "w")
	local rep_cnt = 0
	if f then
		if isEmpty(tRep) then
			f:write("没有重复的时间出现\n")
		else
			local str = ""
			for k,v in pairsByKey(tRep) do
				str = str .. "重复时间:" .. k .. "  重复次数：<" .. v .. ">\n"
				rep_cnt = rep_cnt + 1
			end
			f:write("=================================================\n")
			f:write("== 重复的时间指的是 在同一个时间段出现两次以上的交易。\n")
			f:write("== " .. fileName .. "重复的时间段有" .. rep_cnt .. "个 \n")
			f:write("=================================================\n\n")
			f:write(str)	
		end
		f:close()
	end
	-- 打印缺漏时间
	f = io.open(path .. "缺漏时间.txt", "w")
	local lose_cnt = 0
	if f then
		if isEmpty(tLose) then
			f:write("没有缺漏的时间出现\n")
		else
			local str = ""
			for k,v in pairsByKey(tLose) do
				str = str .. "缺漏时间:" .. k .. "\n"
				lose_cnt = lose_cnt + 1
			end
			f:write("=================================================\n")
			f:write("== 缺漏的时间指的是 在交易时间段上没有的交易数据。\n")
			f:write("== " .. fileName .. "缺失的时间段有" .. lose_cnt .. "个 \n")
			f:write("=================================================\n\n")
			f:write(str)
		end
		f:close()
	end
	-- 打印异常时间
	f = io.open(path .. "异常时间.txt", "w")
	local exp_cnt = 0
	if f then
		if isEmpty(tExp) then
			f:write("没有异常的时间出现\n")
		else
			local str = ""
			for k,v in pairsByKey(tExp) do
				str = str .. "异常时间:" .. k .. "\n"
				exp_cnt = exp_cnt + 1
			end
			f:write("=================================================\n")
			f:write("== 异常的时间指的是 在非交易时间段上出现的交易数据。\n")
			f:write("== " .. fileName .. "异常的时间段有" .. exp_cnt .. "个 \n")
			f:write("=================================================\n\n")
			f:write(str)	
		end
		f:close()
	end
	return rep_cnt,lose_cnt,exp_cnt
end

function main()
	local output_file_name = "分析"..db_table_name.."结果.txt" 
	local sqlStatement
	local tDays = {} -- 保存所有的交易日
	local tAllExp = {} -- 保存所有的异常

	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))

	-- 获取表中所有的交易日
	sqlStatement = string.format([[
		SELECT DISTINCT floor(Time/10000) AS Dates
		FROM %s
		ORDER BY Dates;
	]], db_table_name)
	local cur = con:execute(sqlStatement)
	while true do
		local t = cur:fetch({}, "a")
		if not t then break end
		local time = string.sub(t.Dates, 1,6)
		if not tDays[time] then
			tDays[time] = 1      -- 
		end
	end
	cur:close()
	local tDaySort = sortByKey(tDays)
	
	if isEmpty(tDays) then
		con:close()
		env:close()
		print("可能表" .. db_table_name .. "是张空表")
		return
	end
	
	if not getCurDirAll()(folder_name) then
		os.execute("mkdir " .. folder_name)
	end
	-- 打印在表中的所有的日期
	local totalDays_file = io.open(folder_name .. "/" .."表" .. db_table_name .. "所有日期.txt", "w")
	if totalDays_file then
		totalDays_file:write("表" .. db_table_name .. "涉及到的时间有" .. #tDaySort .. "天：\n")
		for _,v in ipairs(tDaySort) do
			totalDays_file:write(v .. "\n")
		end
		totalDays_file:close()
	end
	
	-- 获取 InstrumentID 的字段名字
	local tFileName = {}   -- 保存文件名
	sqlStatement = string.format([[
		SELECT DISTINCT InstrumentID AS FileName
		FROM %s;
	]],db_table_name)
	local cur = assert(con:execute(sqlStatement))
	while true do
		local t = cur:fetch({}, "a")
		if not t then break end
		tFileName[t.FileName] = true
	end	
	cur:close()
	
	local loseDayForAll = {}  -- 所有都丢失的时间
	local expDayForAll = {}   -- 所有都异常的时间
	-- 分析某个 InstrumentID 的时间情况
	-- bFilter 是否过滤掉都没有的时间
	-- ret 缺失时间, 异常时间
	function analyzeDate(tInsDays, InsName, bFilter)
		-- 分析可能缺漏的时间，过滤掉周末
		-- 需要注意法定的节假日
		local expDays = {} -- 异常时间,如非交易日确有交易数据
		local loseDays = {} -- 可能缺失的时间
		local strTime
		for day in pairsForDate(tDaySort[#tDaySort], tDaySort[1]) do
			strTime = tDay2strDay(day)
			if isTradeDate(day) then
				if not tInsDays[strTime] then
					if bFilter then
						if not loseDayForAll[strTime] then
							table.insert(loseDays, strTime)
						end
					else
						loseDayForAll[strTime] = true
						table.insert(loseDays, strTime)
					end
				end
			else
				if tInsDays[strTime] then
					if bFilter then
						if not expDayForAll[strTime] then
							table.insert(expDays, strTime)
						end
					else
						expDayForAll[strTime] = true
						table.insert(expDays, strTime)
					end
				end
			end
		end
		-- if (#loseDays > 0) or (#expDays > 0) then
			os.execute("md " .. folder_name .. "\\" .. InsName)
		-- end
		-- 打印在表中的缺失的时间
		if #loseDays > 0 then
		local loseDays_file = io.open(folder_name .. "/" .. InsName .. "/" ..  InsName .. "_可能丢失的日期.txt", "w")
			if loseDays_file then
				loseDays_file:write("===================================================\n")
				loseDays_file:write("== 表"..db_table_name .."从时间：" .. tDaySort[#tDaySort] .. " 到时间：" .. tDaySort[1] .. " 涉及的交易日有：" .. #tDaySort .. "天".."\n")
				loseDays_file:write("== 排除掉周六和周天和法定节假日后\n")
				if bFilter then
					loseDays_file:write("== 以及去除在文件 \"相同问题_可能丢失的时间.txt\" 中的时间".."\n")
				end
				loseDays_file:write("== 在这段时间中，有可能缺失的日期\n")
				loseDays_file:write("== 下列时间总计 《" .. #loseDays .. "》天\n")
				loseDays_file:write("===================================================\n\n")
				
				for _,v in ipairs(loseDays) do
					loseDays_file:write(v .. "\n")
				end
				loseDays_file:close()
			end	
		end
		
		-- 打印在表中的异常的时间
		if #expDays > 0 then
			local expDays_file = io.open(folder_name .. "/" .. InsName .. "/" ..  InsName .. "_可能异常的日期.txt", "w")
			if expDays_file then
				expDays_file:write("===================================================\n")
				expDays_file:write("== 表"..db_table_name .."从时间：" .. tDaySort[#tDaySort] .. " 到时间：" .. tDaySort[1] .. " 涉及的交易日有：" .. #tDaySort .. "天".."\n")
				expDays_file:write("== 交易日出现在周六和周天或者法定节假日\n")
				if bFilter then
					expDays_file:write("== 以及去除在文件 \"相同问题_可能异常的时间.txt\" 中的时间".."\n")
				end			
				expDays_file:write("== 下列时间总计 《" .. #expDays .. "》天\n")
				expDays_file:write("===================================================\n\n")
			
				for _,v in ipairs(expDays) do
					expDays_file:write(v .. "\n")
				end
				expDays_file:close()
			end	
		end
		return loseDays, expDays
	end
	
	local tReport = {}  -- 分析报表 name项目名称 loseNum 缺失的数量 expNum 异常的数量
	local t1,t2 = analyzeDate(tDays, "相同问题", false)
	table.insert(tReport, {name = "相同问题", loseNum = #t1, expNum = #t2,repCnt=0, loseCnt=0, expCnt=0})
	local tDefine = {} -- 保存未被定义在 cfgBourse 的合约
	local notBourse = {} -- 不应该在这个表中的合约
	-- 分析物品的时间缺失问题
	for fileName, _ in pairs(tFileName) do
		local flag = string.match(fileName, "(%a+)")
		local bourseKey = cfgBourse[flag]
		if not bourseKey then
			if not tDefine[flag] then
				tDefine[flag] = true
			end
		elseif string.match(bourseKey,"(.-)#.+$") ~= db_table_name then
			if not notBourse[flag] then
				notBourse[flag] = bourseKey
			end			
		else
			local tDays = {}
			local tRepTime = {} --  重复的时间,k时间，v次数
			local tTime = {} -- 不会重复的时间
			tradeTime = cfgTradeTime[bourseKey]
			sqlStatement = string.format([[
				SELECT Time 
				FROM %s
				WHERE InstrumentID = '%s'
				ORDER BY Time;
			]], db_table_name, fileName)
			local cur = con:execute(sqlStatement)
			while true do
				local t = cur:fetch({}, "a")
				if not t then break end
				-- 日期的处理
				local day = string.sub(t.Time, 1,6)
				if not tDays[day] then
					tDays[day] = 1      -- 
				end
				-- 时间处理
				if not tTime[t.Time] then
					tTime[t.Time] = 1
				else
					tTime[t.Time] = tTime[t.Time]+1
					tRepTime[t.Time] = tTime[t.Time]
				end
			end
			cur:close()
			-- 时间处理
			local tLoseTime = {} -- 丢失的时间 tradeTime
			for day in pairs(tDays) do
				for t in pairsForTime(day, tradeTime) do
					if not tTime[t] then
						tLoseTime[t] = true
					else
						tTime[t] = "ok"
					end
				end
			end
			--  异常的时间
			local tExpTime = {} 
			for k, v in pairs(tTime) do
				if v ~= "ok" then
					tExpTime[k] = true
					if not tAllExp[fileName .. "#" .. k] then
						tAllExp[fileName .. "#" .. k] = true
					end
				end
			end
			
			local t1,t2 = analyzeDate(tDays, fileName, true)
			local repcnt,losecnt,expcnt = printTime(fileName,tRepTime, tLoseTime, tExpTime)
			
			-- name-物品名称 loseNum-丢失的天数 expNum-有异常的天数 repcnt-重复的时间数 losecnt-丢失的时间数 expcnt-异常的时间数
			table.insert(tReport, {name = fileName, loseNum = #t1, expNum = #t2, repCnt=repcnt, loseCnt=losecnt, expCnt=expcnt})
			print("finish " .. fileName)
		end
	end
	
	-- 打印分析的总表
	local report_file = io.open(folder_name .. "/" .. db_table_name .. "分析报告.txt", "w")
	if report_file then
		report_file:write("==========================================================\n")
		report_file:write("== 表"..db_table_name .."从时间：" .. tDaySort[#tDaySort] .. " 到时间：" .. tDaySort[1] .. " 涉及的交易日有：" .. #tDaySort .. "天".."\n")
		report_file:write("== 交易日指的是非周六周日和非法定节假日的交易时间\n")
		report_file:write("== \"可能丢失的天数\"意味着在交易日中，却缺失交易数据\n")
		report_file:write("== \"有异常的天数\"意味着在非交易日中，有交易数据\n")
		report_file:write("== \"相同问题\"意味着所有的订单都会出现的问题，必须要优先解决\n")
		report_file:write("==========================================================\n\n")
		for _,v in ipairs(tReport) do
			report_file:write(string.format("  %10s : 可能丢失的天数 : %-6s,有异常的天数 : %-6s,重复的时间数 : %-6d,丢失的时间数 : %-6d,异常的时间数 : %-6d", v.name,v.loseNum,v.expNum,v.repCnt,v.loseCnt,v.expCnt))
			if v.loseNum<=0 and v.expNum <= 0 then
				report_file:write("    ^_^")
			end
			report_file:write("\n")
		end
		report_file:close()
	end
	-- 打印异常表
	local exp_file = io.open(folder_name .. "/" .. "异常时间表.txt", "w")
	if exp_file then
		exp_file:write(db_table_name .. "\n")
		local a,b
		for times in pairs(tAllExp) do
			a,b = string.match(times, "(%w+)#(%w+)")
			exp_file:write(a .. "\t" ..b .. "\n")
		end
		exp_file:close()
	end
	-- 打印未被配置在的合约
	local un_file = io.open(folder_name .. "/" .. "未定义的合约.txt", "w")
	if un_file then
		un_file:write(db_table_name .. "\n")
		for flag in pairs(tDefine) do
			un_file:write(flag .. "\n")
		end
		un_file:close()
	end	
	-- 打印其他表的合约
	local not_file = io.open(folder_name .. "/" .. "应该在其他表的合约.txt", "w")
	if not_file then
		for k, v in pairs(notBourse) do
			not_file:write(k .. "----->" .. v .. "\n")
		end
		not_file:close()
	end	
	
	
	con:close()
	env:close()
end

main()