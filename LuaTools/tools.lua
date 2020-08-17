-- tools.lua
-- ���߰�

require "config"

-- 140317 --> {year=2014, month=3, day=17}
function strDay2tDay(strTime)
	local tTime = {}
	tTime.year = tonumber("20" .. string.sub(strTime,1,2))
	tTime.month = tonumber(string.sub(strTime, 3, 4))
	tTime.day = tonumber(string.sub(strTime, 5, 6))
	return tTime
end

-- {year=2014, month=3, day=17} --> 140317
function tDay2strDay(tTime)
	local year = string.sub(tTime.year, 3,4)
	local month = string.len(tTime.month) < 2 and "0" .. tTime.month or tTime.month
	local day = string.len(tTime.day) < 2 and "0" .. tTime.day or tTime.day
	local strTime =  year .. month .. day
	return strTime
end

-- {year=2014, month=3, day=17, hour=10, min=32} --> 1403171032
function tTime2strTime(tTime)
	local hour = string.len(tTime.hour) < 2 and "0" .. tTime.hour or tTime.hour
	local min = string.len(tTime.min) < 2 and "0" .. tTime.min or tTime.min
	return tDay2strDay(tTime) .. hour .. min
end

-- 1402121451 --> 2014/02/12-14:51
function dbTime2srcTime(time)
	local str = {}
	local index = 1
	while index <= #time do
		table.insert(str,string.sub(time,index,index+1))
		index = index+2
	end
	time = "20" .. str[1] .."/"..str[2].."/"..str[3] .. "-" ..str[4] .. ":" ..str[5]
	return time
end
-- 2014/02/12-14:51 --> 1402121451
function srcTime2dbTime(time)
	local str = string.gsub(time, "[:/-]", "")
	str = string.sub(str,3)
	return str
end

-- OpenPrice HighestPrice LowestPrice  ClosePrice �ӿ⵽Դ����Ӧ�ö���1000
local function dbValue2srcValue(v)
	v = v/1000
	return string.format("%.2f", v)
end

-- OpenPrice HighestPrice LowestPrice  ClosePrice ��Դ���ݵ�������Ӧ�ö���1000
local function srcValue2dbValue(v)
	return v*1000
end

-- 2013/09/02-09:17	4966.00	4966.00	4965.00	4965.00	8.00   -->
-- {Time=130902, OpenPrice=4966.00, HighestPrice=4966.00, LowestPrice=4965.00,ClosePrice=4965.00,Volume=8.00}
function srcRow2dbRow(str)
	local t = {}
	local y,m,d,h,mm
	y,m,d,h,mm,t.OpenPrice,t.HighestPrice,t.LowestPrice,t.ClosePrice,t.Volume = 
	string.match(str,"(%d+)/(%d+)/(%d+)-(%d+):(%d+)%s+(%d+%.%d+)%s+(%d+%.%d+)%s+(%d+%.%d+)%s+(%d+%.%d+)%s+(%d+%.%d+)$")
	if not y then return nil end
	y = string.sub(tostring(y),3)
	t.Time = y .. m .. d .. h .. mm
	t.OpenPrice = srcValue2dbValue(t.OpenPrice)
	t.HighestPrice = srcValue2dbValue(t.HighestPrice)
	t.LowestPrice = srcValue2dbValue(t.LowestPrice)
	t.ClosePrice = srcValue2dbValue(t.ClosePrice)
	return t
end
-- {Time=130902, OpenPrice=4966.00, HighestPrice=4966.00, LowestPrice=4965.00,ClosePrice=4965.00,Volume=8.00}   -->
-- 2013/09/02-09:17	4966.00	4966.00	4965.00	4965.00	8.00
function dbRow2srcRow(t)
	return dbTime2srcTime(t.Time) .. "\t" .. dbValue2srcValue(t.OpenPrice) .. "\t" .. dbValue2srcValue(t.HighestPrice) .. "\t" .. dbValue2srcValue(t.LowestPrice) .. "\t" .. dbValue2srcValue(t.ClosePrice) .. "\t" .. string.format("%.2f",t.Volume)
end


-- ��keyֵ����,����һ������
function sortByKey(t, bAsc)
    local temp = {}
    for n in pairs(t) do table.insert(temp, n) end
 
    if bAsc then
        table.sort(temp)    -- ����
    else
        table.sort(temp, function(a,b) return b<a end)   -- ����
    end
 
    return temp
end

-- �жϱ��Ƿ�Ϊ��
function isEmpty(t)
	for k in pairs(t) do
		return false
	end
	return true
end

-- ��������
-- ֻ�ܶԱ��key�����ֽ�������Ĭ�Ͻ���
function pairsByKey(t, bAsc)
	local temp = {}
	for n in pairs(t) do table.insert(temp, n) end

	if bAsc then
		table.sort(temp)	-- ����
	else
		table.sort(temp, function(a,b) return b<a end)	-- ����
	end

	local i = 0
	return function() i = i + 1; local key = temp[i]; return key, t[key]; end
end

-- ���ڵ�����
-- start  ��ʼʱ��
-- endtime  ����ʱ��
-- ret �����������������ڼ�����е�����
function pairsForDate(start, endtime)
	local t = strDay2tDay(start)
	local tEnd = os.time(strDay2tDay(endtime))
	local timestamp  -- ��ǰ��ʱ���
	local tDay

	return function()
		timestamp = os.time(t)
		tDay = os.date("*t", os.time(t))
		t.day = t.day + 1
		if tEnd >= timestamp then
			return tDay
		end
	end
end

-- 60���Ƽ���
local function calc60(num)
	local temp = num%100
	if temp~=0 and temp%60 == 0 then
		num = num+40
	end
	return num
end
-- ʱ�������
-- day ���� 140331
-- tTimeSec ʱ������� tTimeSec = {["999999"]={{0915,1130}, {1300,1515}}}
-- 999999 ���������֮ǰ�Ľ���ʱ���
-- ret 1403310900
function pairsForTime(day,tTimeSec)
	-- �����������Ӧ��ʱ���
	local tLimitTime
	for k,v in pairsByKey(tTimeSec, true) do
		if day < k then
			tLimitTime = v
			break
		end
	end
	local index = 1
	local proTime = tLimitTime[index][1]  -- �н���ʱ��
	local endTime = tLimitTime[index][2]  -- ������ʱ��
	return function()
		proTime = calc60(proTime)
		if proTime <= endTime then
			local str = string.rep('0', 4-string.len(proTime)) .. proTime
			str = day .. str
			proTime = proTime+1
			return str
		else
			index = index + 1
			if tLimitTime[index] then
				proTime = tLimitTime[index][1]  -- �н���ʱ��
				if tonumber(proTime) < tonumber(endTime) then -- ���һ��
					local t = strDay2tDay(day)
					t.day = t.day+1
					day = tDay2strDay(os.date("*t", os.time(t)))
				end
				endTime = tLimitTime[index][2]  -- ������ʱ��
				local str = string.rep('0', 4-string.len(proTime)) .. proTime
				str = day .. str
				proTime = proTime+1
				return str
			end
		end
	end
end

-- �ж�ʱ���Ƿ�Ϊ������
function isTradeDate(t)
	-- ����ĩͬʱ�Ƿ����ڼ��գ���Ϊ��ĩ
	if cfgTradeDay[t.wday] and (not cfgHoliday[tDay2strDay(t)]) then
		return true
	end
end

-- ͨ��Դ�ļ����֣���Ϥ�����Ľ�����
function getBourseBysrcFile(filename)
	local cha = string.match(filename, "/?(%a+)%d+")
	local bourse = cfgBourse[cha]
	if not bourse then return nil end

	return string.match(bourse, "(.-)#.+$")
end

-- ͨ���ļ���·����ȡ�ļ�����
function getFileNameByPath(path)
	local fileName = string.match(path, "/?(%w+)%.")
	return fileName
end

-- ��õ�ǰ��·���µ����е�txt�ļ�
function getCurDirAllTxt()
	os.execute("ls >> temp")
	local tTxtName = {}
	local f = assert(io.open("temp", "r"))
	local str = f:read("*a")
	f:close()
	for s in string.gmatch(str, "%S+%.txt") do
		table.insert(tTxtName, s)
	end
	os.remove("temp")
	return tTxtName
end

-- ��õ�ǰ·���µ����е��ļ�
-- �ж�·���Ƿ���ڵ�ǰ���ļ�����
function getCurDirAll()
	os.execute("ls >> temp")
	local tAllName = {}
	local f = assert(io.open("temp", "r"))
	local str = f:read("*a")
	f:close()
	for s in string.gmatch(str, "%S+") do
		tAllName[str] = true
		-- print(str)
	end
	os.remove("temp")
	return function(FolderName)
		return tAllName[FolderName]
	end
end



