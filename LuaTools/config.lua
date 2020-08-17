-- 配置文件
-- config.lua

-- 各个交易所(表)，每天的交易时间
cfgTradeTime = {}  -- 每天的交易时间
cfgTradeTime["hq_cffex_k1#cffex"] = {["999999"]={{0915,1130}, {1300,1515}}}
cfgTradeTime["hq_czce_k1#czce"] = {["999999"]={{0900,1015}, {1030, 1130}, {1330,1500}}}
cfgTradeTime["hq_dce_k1#dce"] = {["999999"] = {{0900,1015}, {1030, 1130}, {1330,1500}}}
cfgTradeTime["hq_shfe_k1#shfe"] = {["100710"]={{0900,1015}, {1030, 1130}, {1330,1500}},
["999999"]={{0900,1015},{1030,1130},{1330,1500}}}
cfgTradeTime["hq_shfe_k1#shfe_gs"] = {["100701"]={{0900,1015},{1030,1130},{1330,1410},{1420,1500}},
["130705"]={{0900,1015},{1030,1130},{1330,1500}},
["999999"]={{0900,1015},{1030,1130},{1330,1500},{2100,2400},{0000,0230}}}
cfgTradeTime["hq_shfe_k1#shfe_nfm"] = {
["100701"]={{0900,1015},{1030,1130},{1330,1410},{1420,1500}},
["131220"]={{0900,1015},{1030,1130},{1330,1500}},
["999999"]={{0900,1015},{1030,1130},{1330,1500},{2100,2400},{0000,0100}}
}

-- 源文件名字划分交易所
-- 区分大小写
-- 要保证传进工具中的源文件在这里有配置，否则，写入库中的表只能使用默认值
local t = {} 
t["hq_cffex_k1"] = {["#cffex"]={"IF","TF"}}
t["hq_czce_k1"] = {["#czce"]={"CF","ER","FG","JR","ME","OI","PM","RI","RM","RO","RS","SR","TA","TC","WH","WS","WT"}}
t["hq_dce_k1"] = {["#dce"]={"a","b","bb","c","fb","i","j","JD","JM","l","m","p","pp","v","y"}}
t["hq_shfe_k1"] = {["#shfe"]={"bu","fu","hc","RB","RU","wr","ru","rb"},["#shfe_gs"]={"AU","AG","ag","au"},["#shfe_nfm"]={"AL","al"}}
cfgBourse = {}
for k, v in pairs(t) do
	for kk,vv in pairs(v) do
		for kkk, vvv in pairs(vv) do
			cfgBourse[vvv] = k .. kk
		end
	end
end


-- 判定是否交易日，周六周天非交易日
cfgTradeDay = {false,true,true,true,true,true,false}

-- 法定节假日
cfgHoliday = {}
cfgHoliday["130610"] = true -- 端午节
cfgHoliday["130611"] = true -- 端午节
cfgHoliday["130612"] = true -- 端午节
cfgHoliday["130919"] = true -- 中秋节
cfgHoliday["130920"] = true -- 中秋节
cfgHoliday["131001"] = true -- 国庆节
cfgHoliday["131002"] = true -- 国庆节
cfgHoliday["131003"] = true -- 国庆节
cfgHoliday["131004"] = true -- 国庆节
cfgHoliday["131007"] = true -- 国庆节
cfgHoliday["140101"] = true -- 元旦
cfgHoliday["140131"] = true -- 春节
cfgHoliday["140203"] = true -- 春节
cfgHoliday["140204"] = true -- 春节
cfgHoliday["140205"] = true -- 春节
cfgHoliday["140206"] = true -- 春节
cfgHoliday["140214"] = true -- 元宵节


