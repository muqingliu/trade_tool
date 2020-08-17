-- �����ļ�
-- config.lua

-- ����������(��)��ÿ��Ľ���ʱ��
cfgTradeTime = {}  -- ÿ��Ľ���ʱ��
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

-- Դ�ļ����ֻ��ֽ�����
-- ���ִ�Сд
-- Ҫ��֤���������е�Դ�ļ������������ã�����д����еı�ֻ��ʹ��Ĭ��ֵ
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


-- �ж��Ƿ����գ���������ǽ�����
cfgTradeDay = {false,true,true,true,true,true,false}

-- �����ڼ���
cfgHoliday = {}
cfgHoliday["130610"] = true -- �����
cfgHoliday["130611"] = true -- �����
cfgHoliday["130612"] = true -- �����
cfgHoliday["130919"] = true -- �����
cfgHoliday["130920"] = true -- �����
cfgHoliday["131001"] = true -- �����
cfgHoliday["131002"] = true -- �����
cfgHoliday["131003"] = true -- �����
cfgHoliday["131004"] = true -- �����
cfgHoliday["131007"] = true -- �����
cfgHoliday["140101"] = true -- Ԫ��
cfgHoliday["140131"] = true -- ����
cfgHoliday["140203"] = true -- ����
cfgHoliday["140204"] = true -- ����
cfgHoliday["140205"] = true -- ����
cfgHoliday["140206"] = true -- ����
cfgHoliday["140214"] = true -- Ԫ����


