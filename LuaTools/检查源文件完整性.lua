--------------------------------------------------------------
-- ��Ҫ���Դ�ļ�������ʱ���ϵ�������
-- ������ݣ�ȱʧʱ�䡢ȱʧ���ڡ��쳣ʱ�䡢�ظ�ʱ��
-- SRC_FILE ������Ҫ����Դ�ļ������Ϊ�գ����ȡ��ǰ�ļ��µ�����.txt�ļ���ΪԴ�ļ�
-- output_floder �ѷ�����������ڵ��ļ���
-- �����ѡ� ��ȫ���ߣ� ����Ӱ�쵽���ݿ�����
--------------------------------------------------------------
require "tools"

local SRC_FILE = {}

local output_floder = "Դ�ļ�����"  


-----------------------------------------------------------------------------------------
--               ���´����ڲ����������£��벻Ҫ�����޸�
-----------------------------------------------------------------------------------------

-- ��ӡ����
function printReport(tReport, tUnFile)
	-- �ж��Ƿ����ͬ�����ļ���
	if not getCurDirAll()(output_floder) then
		os.execute("mkdir " .. output_floder)
	end
	for k,v in pairs(tReport) do
		local file_name = string.sub(k,1,-5)
		print("output_floder/" .. file_name .. "Դ�ļ�����.txt")
		local f = io.open(output_floder .. "/" .. file_name .. "Դ�ļ�����.txt", "w")
		if f then
			f:write("==============================\n")
			f:write("        ��ʧ������\n")
			f:write("==============================\n")
			for k,v in ipairs(v.LoseDay) do
				f:write("��ʧ������: " .. v .. "\n")
			end
			
			f:write("\n==============================\n")
			f:write("        �쳣������\n")
			f:write("==============================\n")
			for k,v in ipairs(v.ExpDay) do
				f:write("�쳣������: " .. v .. "\n")
			end		

			f:write("\n==============================\n")
			f:write("        �ظ�ʱ��Ĵ���\n")
			f:write("==============================\n")
			for k,v in pairsByKey(v.RepTime) do
				f:write("�ظ�ʱ�䣺" .. dbTime2srcTime(k) .. "  ������" .. v .. "\n")
			end		
			
			f:write("\n==============================\n")
			f:write("        ȱʧ��ʱ��\n")
			f:write("==============================\n")
			for k,v in pairsByKey(v.LoseTime) do
				f:write("ȱʧʱ�䣺" .. dbTime2srcTime(k) .. "\n")
			end		

			f:write("\n==============================\n")
			f:write("        �쳣��ʱ��\n")
			f:write("==============================\n")
			for k,v in pairsByKey(v.ExpTime) do
				f:write("�쳣ʱ�䣺" .. dbTime2srcTime(k) .. "\n")
			end					
			
			f:close()
		end
	end
	-- ��ӡδʶ����ļ�
	if #tUnFile > 0 then
		local f = assert(io.open(output_floder .. "/" .. "δʶ����ļ�.txt", "w"))
		for k,v in ipairs(tUnFile) do
			f:write(v .. "\n")
		end
		f:close()
	end	
end

function main ()
	local tReport = {} -- ��������
	local tUnFile={} -- ��֤��֪���������ű������Դ�ļ�
	-- ���SRC_FILEû���ļ������ȡ��ǰ·���µ�txt�ļ�
	if #SRC_FILE == 0 then
		SRC_FILE = getCurDirAllTxt()
	end
	for _,v in pairs(SRC_FILE) do
		local bourse = getBourseBysrcFile(v) -- ��ȡ������
		if not bourse then 
			-- bourse = defaule_bourse
			table.insert(tUnFile, v)
		else
			local f = assert(io.open(v,"r"))
			local t = {}
			t.RepTime = {}  -- �ظ�ʱ�� k ʱ�� v ����
			t.LoseTime = {} -- ȱʧ��ʱ�� k ʱ�� v true
			t.ExpTime = {}  -- �����쳣��ʱ�� k ʱ�� v true
			t.day = {}      -- Դ�ļ����漰�������� k ���� v TRUE
			t.LoseDay = {}  -- ��ʧ������ k num v ����
			t.ExpDay = {}   -- �쳣������ k num v ����
			local tTime = {}  -- ����Դ�ļ��е����в��ظ���ʱ�� k ʱ�� v����
			local flag = string.match(v, "(%a+)")
			local tradeTime = cfgTradeTime[cfgBourse[flag]]
			-- tradeTime = cfgTradeTime[bourse]  -- ����ʱ��
			
			while true do
				local l = f:read()
				if not l then break end
				local str = string.match(l,"^(%d+/%d+/%d+-%d+:%d+)%s+%d+%.%d+%s+%d+%.%d+%s+%d+%.%d+%s+%d+%.%d+%s+%d+%.%d+$")
				if str then
					str = srcTime2dbTime(str)
					-- �����ظ�ʱ��
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
			-- ���ڴ���
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
			
			-- ʱ�䴦��
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
			--  �쳣��ʱ��
			for k, v in pairs(tTime) do
				if v ~= "ok" then
					t.ExpTime[k] = true
				end
			end
			
			tReport[v] = t
			print("finish " .. v)
		end
	end
	-- ��ӡ����
	printReport(tReport,tUnFile)
end

main()

