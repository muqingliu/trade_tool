------------------------------------------------------------
-- ����Դ�ļ�����ͬ���ݿ����ݶԱȣ�����Դ�ļ����в��첹��
-- INSERT_FILE ������Ҫ����Դ�ļ������Ϊ�գ����ȡ��ǰ�ļ��µ�����.txt�ļ���ΪԴ�ļ�
-- output_floder ����ļ���
-- ����ļ������ 'δʶ����ļ�.txt' ��ζ����Ʒ��config.lua��δ������
-- �����ѡ� �Ŀ⹤�ߣ� ���޸ĵ����ݿ�����
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
local output_floder = "����ݿ�����"

-----------------------------------------------------------------------------------------
--               ���´����ڲ����������£��벻Ҫ�����޸�
-----------------------------------------------------------------------------------------

-- ��������
function insertDB(con, tDiff, tUnFile)
	os.execute("mkdir " .. output_floder)
	if not isEmpty(tDiff) then
		for bourse, v in pairs(tDiff) do  -- ��ý�����
			os.execute("md " .. output_floder .. "\\" .. bourse)
			local strValue = ""
			local sql = "INSERT INTO " .. bourse .. " (InstrumentID,Time,OpenPrice,HighestPrice,LowestPrice,ClosePrice,Volume) VALUES "
			for ins,t in pairs(v) do   -- ��ö���
				if not isEmpty(t) then
					local f = io.open(output_floder .. "/" .. bourse .. "/" .. ins .. ".txt", "w")
					for _, vv in ipairs(t) do    -- ��ü�¼
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
		print("û����Ҫд�����ݿ������")
	end	
	
	if #tUnFile > 0 then
		local f = assert(io.open(output_floder .. "/" .. "δʶ����ļ�.txt", "w"))
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
	local tDiff = {} -- ����д����е����� k-str-������ v-table-��¼
	local tUnFile={} -- ��֤��֪���������ű������Դ�ļ�
	for _, filepath in pairs(INSERT_FILE) do
		print("---------->" .. filepath)
		local bourse = getBourseBysrcFile(filepath) -- ��ȡ������
		if not bourse then 
			table.insert(tUnFile, filepath)
		else
			local ins = getFileNameByPath(filepath)
			-- ���ж�ȡ����
			local cur = con:execute(string.format([[
				SELECT InstrumentID,Time,OpenPrice,HighestPrice,LowestPrice,ClosePrice,Volume 
				FROM %s
				WHERE InstrumentID = '%s';
			]],bourse,ins))
			local tDBInfo = {}   -- ����Դ�������� k Time,v {}
			while true do
				local t = cur:fetch({}, "a")
				if not t then break end
				tDBInfo[t.Time] = t
			end
			cur:close()
			-- Դ�ļ��ж�ȡ����
			local tSrcInfo = {}  -- Դ�ļ��������� k Time,v {}
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
			-- �Ƚϲ���д��
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
