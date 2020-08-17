------------------------------------------------------------
-- ��Ҫ������ݿ�������ָ�����ʱ���ϵ�������
-- ������ݣ�1�������������ڵĲ������۳��������պ�����������
--           2�����ݽ������Ľ���ʱ�䣬���ʱ���ȱ©���쳣���ظ������
-- db_table_name ָ�����ı��ñ�����Ϊ����������
-- folder_name ������ɺ�������ļ�Ŀ¼
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

local db_table_name = "hq_shfe_k1"
local folder_name = "����"..db_table_name.."���"  -- ����ļ�������

-----------------------------------------------------------------------------------------
--               ���´����ڲ����������£��벻Ҫ�����޸�
-----------------------------------------------------------------------------------------

-- local tradeTime = cfgTradeTime[db_table_name]
local tradeTime 
-- ��ӡʱ���������
-- tRep �ظ�ʱ�� k ʱ�� v ����
-- tLose ȱ©��ʱ�� k ʱ�� v true
-- tExp ���쳣��ʱ�� k ʱ�� v true
-- ret tRep���� tLose���� tExp����
function printTime(fileName,tRep, tLose, tExp)
	local path = folder_name .. "/" .. fileName .. "/"
	-- ��ӡ�ظ�ʱ��
	local f = io.open(path .. "�ظ�ʱ��.txt", "w")
	local rep_cnt = 0
	if f then
		if isEmpty(tRep) then
			f:write("û���ظ���ʱ�����\n")
		else
			local str = ""
			for k,v in pairsByKey(tRep) do
				str = str .. "�ظ�ʱ��:" .. k .. "  �ظ�������<" .. v .. ">\n"
				rep_cnt = rep_cnt + 1
			end
			f:write("=================================================\n")
			f:write("== �ظ���ʱ��ָ���� ��ͬһ��ʱ��γ����������ϵĽ��ס�\n")
			f:write("== " .. fileName .. "�ظ���ʱ�����" .. rep_cnt .. "�� \n")
			f:write("=================================================\n\n")
			f:write(str)	
		end
		f:close()
	end
	-- ��ӡȱ©ʱ��
	f = io.open(path .. "ȱ©ʱ��.txt", "w")
	local lose_cnt = 0
	if f then
		if isEmpty(tLose) then
			f:write("û��ȱ©��ʱ�����\n")
		else
			local str = ""
			for k,v in pairsByKey(tLose) do
				str = str .. "ȱ©ʱ��:" .. k .. "\n"
				lose_cnt = lose_cnt + 1
			end
			f:write("=================================================\n")
			f:write("== ȱ©��ʱ��ָ���� �ڽ���ʱ�����û�еĽ������ݡ�\n")
			f:write("== " .. fileName .. "ȱʧ��ʱ�����" .. lose_cnt .. "�� \n")
			f:write("=================================================\n\n")
			f:write(str)
		end
		f:close()
	end
	-- ��ӡ�쳣ʱ��
	f = io.open(path .. "�쳣ʱ��.txt", "w")
	local exp_cnt = 0
	if f then
		if isEmpty(tExp) then
			f:write("û���쳣��ʱ�����\n")
		else
			local str = ""
			for k,v in pairsByKey(tExp) do
				str = str .. "�쳣ʱ��:" .. k .. "\n"
				exp_cnt = exp_cnt + 1
			end
			f:write("=================================================\n")
			f:write("== �쳣��ʱ��ָ���� �ڷǽ���ʱ����ϳ��ֵĽ������ݡ�\n")
			f:write("== " .. fileName .. "�쳣��ʱ�����" .. exp_cnt .. "�� \n")
			f:write("=================================================\n\n")
			f:write(str)	
		end
		f:close()
	end
	return rep_cnt,lose_cnt,exp_cnt
end

function main()
	local output_file_name = "����"..db_table_name.."���.txt" 
	local sqlStatement
	local tDays = {} -- �������еĽ�����
	local tAllExp = {} -- �������е��쳣

	local env = luasql.mysql()
	local con = assert(env:connect(db_dbase, db_user, db_pwd, db_host,db_port))

	-- ��ȡ�������еĽ�����
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
		print("���ܱ�" .. db_table_name .. "���ſձ�")
		return
	end
	
	if not getCurDirAll()(folder_name) then
		os.execute("mkdir " .. folder_name)
	end
	-- ��ӡ�ڱ��е����е�����
	local totalDays_file = io.open(folder_name .. "/" .."��" .. db_table_name .. "��������.txt", "w")
	if totalDays_file then
		totalDays_file:write("��" .. db_table_name .. "�漰����ʱ����" .. #tDaySort .. "�죺\n")
		for _,v in ipairs(tDaySort) do
			totalDays_file:write(v .. "\n")
		end
		totalDays_file:close()
	end
	
	-- ��ȡ InstrumentID ���ֶ�����
	local tFileName = {}   -- �����ļ���
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
	
	local loseDayForAll = {}  -- ���ж���ʧ��ʱ��
	local expDayForAll = {}   -- ���ж��쳣��ʱ��
	-- ����ĳ�� InstrumentID ��ʱ�����
	-- bFilter �Ƿ���˵���û�е�ʱ��
	-- ret ȱʧʱ��, �쳣ʱ��
	function analyzeDate(tInsDays, InsName, bFilter)
		-- ��������ȱ©��ʱ�䣬���˵���ĩ
		-- ��Ҫע�ⷨ���Ľڼ���
		local expDays = {} -- �쳣ʱ��,��ǽ�����ȷ�н�������
		local loseDays = {} -- ����ȱʧ��ʱ��
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
		-- ��ӡ�ڱ��е�ȱʧ��ʱ��
		if #loseDays > 0 then
		local loseDays_file = io.open(folder_name .. "/" .. InsName .. "/" ..  InsName .. "_���ܶ�ʧ������.txt", "w")
			if loseDays_file then
				loseDays_file:write("===================================================\n")
				loseDays_file:write("== ��"..db_table_name .."��ʱ�䣺" .. tDaySort[#tDaySort] .. " ��ʱ�䣺" .. tDaySort[1] .. " �漰�Ľ������У�" .. #tDaySort .. "��".."\n")
				loseDays_file:write("== �ų�������������ͷ����ڼ��պ�\n")
				if bFilter then
					loseDays_file:write("== �Լ�ȥ�����ļ� \"��ͬ����_���ܶ�ʧ��ʱ��.txt\" �е�ʱ��".."\n")
				end
				loseDays_file:write("== �����ʱ���У��п���ȱʧ������\n")
				loseDays_file:write("== ����ʱ���ܼ� ��" .. #loseDays .. "����\n")
				loseDays_file:write("===================================================\n\n")
				
				for _,v in ipairs(loseDays) do
					loseDays_file:write(v .. "\n")
				end
				loseDays_file:close()
			end	
		end
		
		-- ��ӡ�ڱ��е��쳣��ʱ��
		if #expDays > 0 then
			local expDays_file = io.open(folder_name .. "/" .. InsName .. "/" ..  InsName .. "_�����쳣������.txt", "w")
			if expDays_file then
				expDays_file:write("===================================================\n")
				expDays_file:write("== ��"..db_table_name .."��ʱ�䣺" .. tDaySort[#tDaySort] .. " ��ʱ�䣺" .. tDaySort[1] .. " �漰�Ľ������У�" .. #tDaySort .. "��".."\n")
				expDays_file:write("== �����ճ�����������������߷����ڼ���\n")
				if bFilter then
					expDays_file:write("== �Լ�ȥ�����ļ� \"��ͬ����_�����쳣��ʱ��.txt\" �е�ʱ��".."\n")
				end			
				expDays_file:write("== ����ʱ���ܼ� ��" .. #expDays .. "����\n")
				expDays_file:write("===================================================\n\n")
			
				for _,v in ipairs(expDays) do
					expDays_file:write(v .. "\n")
				end
				expDays_file:close()
			end	
		end
		return loseDays, expDays
	end
	
	local tReport = {}  -- �������� name��Ŀ���� loseNum ȱʧ������ expNum �쳣������
	local t1,t2 = analyzeDate(tDays, "��ͬ����", false)
	table.insert(tReport, {name = "��ͬ����", loseNum = #t1, expNum = #t2,repCnt=0, loseCnt=0, expCnt=0})
	local tDefine = {} -- ����δ�������� cfgBourse �ĺ�Լ
	local notBourse = {} -- ��Ӧ����������еĺ�Լ
	-- ������Ʒ��ʱ��ȱʧ����
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
			local tRepTime = {} --  �ظ���ʱ��,kʱ�䣬v����
			local tTime = {} -- �����ظ���ʱ��
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
				-- ���ڵĴ���
				local day = string.sub(t.Time, 1,6)
				if not tDays[day] then
					tDays[day] = 1      -- 
				end
				-- ʱ�䴦��
				if not tTime[t.Time] then
					tTime[t.Time] = 1
				else
					tTime[t.Time] = tTime[t.Time]+1
					tRepTime[t.Time] = tTime[t.Time]
				end
			end
			cur:close()
			-- ʱ�䴦��
			local tLoseTime = {} -- ��ʧ��ʱ�� tradeTime
			for day in pairs(tDays) do
				for t in pairsForTime(day, tradeTime) do
					if not tTime[t] then
						tLoseTime[t] = true
					else
						tTime[t] = "ok"
					end
				end
			end
			--  �쳣��ʱ��
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
			
			-- name-��Ʒ���� loseNum-��ʧ������ expNum-���쳣������ repcnt-�ظ���ʱ���� losecnt-��ʧ��ʱ���� expcnt-�쳣��ʱ����
			table.insert(tReport, {name = fileName, loseNum = #t1, expNum = #t2, repCnt=repcnt, loseCnt=losecnt, expCnt=expcnt})
			print("finish " .. fileName)
		end
	end
	
	-- ��ӡ�������ܱ�
	local report_file = io.open(folder_name .. "/" .. db_table_name .. "��������.txt", "w")
	if report_file then
		report_file:write("==========================================================\n")
		report_file:write("== ��"..db_table_name .."��ʱ�䣺" .. tDaySort[#tDaySort] .. " ��ʱ�䣺" .. tDaySort[1] .. " �漰�Ľ������У�" .. #tDaySort .. "��".."\n")
		report_file:write("== ������ָ���Ƿ��������պͷǷ����ڼ��յĽ���ʱ��\n")
		report_file:write("== \"���ܶ�ʧ������\"��ζ���ڽ������У�ȴȱʧ��������\n")
		report_file:write("== \"���쳣������\"��ζ���ڷǽ������У��н�������\n")
		report_file:write("== \"��ͬ����\"��ζ�����еĶ���������ֵ����⣬����Ҫ���Ƚ��\n")
		report_file:write("==========================================================\n\n")
		for _,v in ipairs(tReport) do
			report_file:write(string.format("  %10s : ���ܶ�ʧ������ : %-6s,���쳣������ : %-6s,�ظ���ʱ���� : %-6d,��ʧ��ʱ���� : %-6d,�쳣��ʱ���� : %-6d", v.name,v.loseNum,v.expNum,v.repCnt,v.loseCnt,v.expCnt))
			if v.loseNum<=0 and v.expNum <= 0 then
				report_file:write("    ^_^")
			end
			report_file:write("\n")
		end
		report_file:close()
	end
	-- ��ӡ�쳣��
	local exp_file = io.open(folder_name .. "/" .. "�쳣ʱ���.txt", "w")
	if exp_file then
		exp_file:write(db_table_name .. "\n")
		local a,b
		for times in pairs(tAllExp) do
			a,b = string.match(times, "(%w+)#(%w+)")
			exp_file:write(a .. "\t" ..b .. "\n")
		end
		exp_file:close()
	end
	-- ��ӡδ�������ڵĺ�Լ
	local un_file = io.open(folder_name .. "/" .. "δ����ĺ�Լ.txt", "w")
	if un_file then
		un_file:write(db_table_name .. "\n")
		for flag in pairs(tDefine) do
			un_file:write(flag .. "\n")
		end
		un_file:close()
	end	
	-- ��ӡ������ĺ�Լ
	local not_file = io.open(folder_name .. "/" .. "Ӧ����������ĺ�Լ.txt", "w")
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