--------------------------------------------------------------
-- 主要检查源文件数据在时间上的延续性
-- 检查内容：缺失时间、缺失日期、异常时间、重复时间
-- SRC_FILE 保存需要检查的源文件，如果为空，则获取当前文件下的所有.txt文件作为源文件
-- output_floder 把分析结果保存在的文件夹
-- 【提醒】 安全工具， 不会影响到数据库数据
--------------------------------------------------------------
require "tools"

local SRC_FILE = {}

local output_floder = "源文件分析"  


-----------------------------------------------------------------------------------------
--               以下代码在不清楚的情况下，请不要随意修改
-----------------------------------------------------------------------------------------

-- 打印报表
function printReport(tReport, tUnFile)
	-- 判断是否存在同名的文件夹
	if not getCurDirAll()(output_floder) then
		os.execute("mkdir " .. output_floder)
	end
	for k,v in pairs(tReport) do
		local file_name = string.sub(k,1,-5)
		print("output_floder/" .. file_name .. "源文件分析.txt")
		local f = io.open(output_floder .. "/" .. file_name .. "源文件分析.txt", "w")
		if f then
			f:write("==============================\n")
			f:write("        丢失的日期\n")
			f:write("==============================\n")
			for k,v in ipairs(v.LoseDay) do
				f:write("丢失的日期: " .. v .. "\n")
			end
			
			f:write("\n==============================\n")
			f:write("        异常的日期\n")
			f:write("==============================\n")
			for k,v in ipairs(v.ExpDay) do
				f:write("异常的日期: " .. v .. "\n")
			end		

			f:write("\n==============================\n")
			f:write("        重复时间的次数\n")
			f:write("==============================\n")
			for k,v in pairsByKey(v.RepTime) do
				f:write("重复时间：" .. dbTime2srcTime(k) .. "  次数：" .. v .. "\n")
			end		
			
			f:write("\n==============================\n")
			f:write("        缺失的时间\n")
			f:write("==============================\n")
			for k,v in pairsByKey(v.LoseTime) do
				f:write("缺失时间：" .. dbTime2srcTime(k) .. "\n")
			end		

			f:write("\n==============================\n")
			f:write("        异常的时间\n")
			f:write("==============================\n")
			for k,v in pairsByKey(v.ExpTime) do
				f:write("异常时间：" .. dbTime2srcTime(k) .. "\n")
			end					
			
			f:close()
		end
	end
	-- 打印未识别的文件
	if #tUnFile > 0 then
		local f = assert(io.open(output_floder .. "/" .. "未识别的文件.txt", "w"))
		for k,v in ipairs(tUnFile) do
			f:write(v .. "\n")
		end
		f:close()
	end	
end

function main ()
	local tReport = {} -- 分析报表
	local tUnFile={} -- 保证不知道放在那张表的数据源文件
	-- 如果SRC_FILE没有文件，则获取当前路径下的txt文件
	if #SRC_FILE == 0 then
		SRC_FILE = getCurDirAllTxt()
	end
	for _,v in pairs(SRC_FILE) do
		local bourse = getBourseBysrcFile(v) -- 获取交易所
		if not bourse then 
			-- bourse = defaule_bourse
			table.insert(tUnFile, v)
		else
			local f = assert(io.open(v,"r"))
			local t = {}
			t.RepTime = {}  -- 重复时间 k 时间 v 次数
			t.LoseTime = {} -- 缺失的时间 k 时间 v true
			t.ExpTime = {}  -- 可能异常的时间 k 时间 v true
			t.day = {}      -- 源文件中涉及到的日期 k 日期 v TRUE
			t.LoseDay = {}  -- 丢失的日期 k num v 日期
			t.ExpDay = {}   -- 异常的日期 k num v 日期
			local tTime = {}  -- 保存源文件中的所有不重复的时间 k 时间 v次数
			local flag = string.match(v, "(%a+)")
			local tradeTime = cfgTradeTime[cfgBourse[flag]]
			-- tradeTime = cfgTradeTime[bourse]  -- 交易时间
			
			while true do
				local l = f:read()
				if not l then break end
				local str = string.match(l,"^(%d+/%d+/%d+-%d+:%d+)%s+%d+%.%d+%s+%d+%.%d+%s+%d+%.%d+%s+%d+%.%d+%s+%d+%.%d+$")
				if str then
					str = srcTime2dbTime(str)
					-- 查找重复时间
					if not tTime[str] then
						tTime[str] = 1
					else
						tTime[str] = tTime[str] + 1
						t.RepTime[str] = tTime[str]
					end
					local strDay = string.sub(str, 1,6)
					if not t.day[strDay] then
						t.day[strDay] = true
					end
				end
			end
			f:close()
			-- 日期处理
			local tDaySort = sortByKey(t.day)
			for day in pairsForDate(tDaySort[#tDaySort], tDaySort[1]) do
				local strTime = tDay2strDay(day)
				if isTradeDate(day) then
					if not t.day[strTime] then
						table.insert(t.LoseDay, strTime)
					end
				else
					if t.day[strTime] then
						table.insert(t.ExpDay, strTime)
					end
				end
			end
			
			-- 时间处理
			local cnt = 0
			for day in pairs(t.day) do
				for strtime in pairsForTime(day, tradeTime) do
					if cnt<20 then
						cnt = cnt + 1
					end
					if not tTime[strtime] then
						t.LoseTime[strtime] = true
					else
						tTime[strtime] = "ok"
					end
				end
			end
			--  异常的时间
			for k, v in pairs(tTime) do
				if v ~= "ok" then
					t.ExpTime[k] = true
				end
			end
			
			tReport[v] = t
			print("finish " .. v)
		end
	end
	-- 打印报告
	printReport(tReport,tUnFile)
end

main()

