-- tools.lua
-- 工具包

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

-- OpenPrice HighestPrice LowestPrice  ClosePrice 从库到源数据应该都除1000
local function dbValue2srcValue(v)
	v = v/1000
	return string.format("%.2f", v)
end

-- OpenPrice HighestPrice LowestPrice  ClosePrice 从源数据到库数据应该都乘1000
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


-- 按key值排序,返回一个数组
function sortByKey(t, bAsc)
    local temp = {}
    for n in pairs(t) do table.insert(temp, n) end
 
    if bAsc then
        table.sort(temp)    -- 升序
    else
        table.sort(temp, function(a,b) return b<a end)   -- 降序
    end
 
    return temp
end

-- 判断表是否为空
function isEmpty(t)
	for k in pairs(t) do
		return false
	end
	return true
end

-- 迭代函数
-- 只能对表的key是数字进行排序，默认降序
function pairsByKey(t, bAsc)
	local temp = {}
	for n in pairs(t) do table.insert(temp, n) end

	if bAsc then
		table.sort(temp)	-- 升序
	else
		table.sort(temp, function(a,b) return b<a end)	-- 降序
	end

	local i = 0
	return function() i = i + 1; local key = temp[i]; return key, t[key]; end
end

-- 日期迭代器
-- start  开始时间
-- endtime  结束时间
-- ret 函数迭代器，返回期间的所有的日期
function pairsForDate(start, endtime)
	local t = strDay2tDay(start)
	local tEnd = os.time(strDay2tDay(endtime))
	local timestamp  -- 当前的时间戳
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

-- 60进制计算
local function calc60(num)
	local temp = num%100
	if temp~=0 and temp%60 == 0 then
		num = num+40
	end
	return num
end
-- 时间迭代器
-- day 日期 140331
-- tTimeSec 时间的区间 tTimeSec = {["999999"]={{0915,1130}, {1300,1515}}}
-- 999999 在这个日期之前的交易时间段
-- ret 1403310900
function pairsForTime(day,tTimeSec)
	-- 获得日期所对应的时间段
	local tLimitTime
	for k,v in pairsByKey(tTimeSec, true) do
		if day < k then
			tLimitTime = v
			break
		end
	end
	local index = 1
	local proTime = tLimitTime[index][1]  -- 行进的时间
	local endTime = tLimitTime[index][2]  -- 结束的时间
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
				proTime = tLimitTime[index][1]  -- 行进的时间
				if tonumber(proTime) < tonumber(endTime) then -- 跨过一天
					local t = strDay2tDay(day)
					t.day = t.day+1
					day = tDay2strDay(os.date("*t", os.time(t)))
				end
				endTime = tLimitTime[index][2]  -- 结束的时间
				local str = string.rep('0', 4-string.len(proTime)) .. proTime
				str = day .. str
				proTime = proTime+1
				return str
			end
		end
	end
end

-- 判断时间是否为交易日
function isTradeDate(t)
	-- 非周末同时非法定节假日，则为周末
	if cfgTradeDay[t.wday] and (not cfgHoliday[tDay2strDay(t)]) then
		return true
	end
end

-- 通过源文件名字，获悉所属的交易所
function getBourseBysrcFile(filename)
	local cha = string.match(filename, "/?(%a+)%d+")
	local bourse = cfgBourse[cha]
	if not bourse then return nil end

	return string.match(bourse, "(.-)#.+$")
end

-- 通过文件的路径获取文件名字
function getFileNameByPath(path)
	local fileName = string.match(path, "/?(%w+)%.")
	return fileName
end

-- 获得当前的路径下的所有的txt文件
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

-- 获得当前路径下的所有的文件
-- 判断路径是否存在当前的文件夹中
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



