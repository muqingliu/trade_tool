DROP TABLE IF EXISTS `Instrument_info`;
DROP TABLE IF EXISTS `Instrument_details`;
DROP TABLE IF EXISTS `Future_redetails`;


CREATE TABLE `Instrument_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长',
  `InstrumentsName` varchar(20)  COMMENT '合约名称',
  `Exchange` varchar(20) COMMENT '交易所',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT '合约-交易所信息表';

CREATE TABLE `Instrument_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长',
  `InstrumentsName` varchar(20)  COMMENT '合约名称',
  `Period` varchar(20)  COMMENT '期数',
  `BeginTime` varchar(20)   COMMENT '起始时间',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT '合约详表';

CREATE TABLE `Future_redetails` (
  `id` int(4) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `InstrumentsName` varchar(32) NOT NULL DEFAULT '',
  `Time` int(4) unsigned zerofill NOT NULL DEFAULT '0000',
  `OpenPrice` float unsigned NOT NULL DEFAULT '0',
  `ClosePrice` float unsigned NOT NULL DEFAULT '0',
  `HighestPrice` float unsigned NOT NULL DEFAULT '0',
  `LowestPrice` float unsigned NOT NULL DEFAULT '0',
  `rOpenPrice` float unsigned NOT NULL DEFAULT '0',
  `rClosePrice` float unsigned NOT NULL DEFAULT '0',
  `rHighestPrice` float unsigned NOT NULL DEFAULT '0',
  `rLowestPrice` float unsigned NOT NULL DEFAULT '0',
  `Volume` int(4) unsigned zerofill NOT NULL DEFAULT '0000',
  PRIMARY KEY (`id`),
  UNIQUE KEY `InstrumentsName_Time` (`InstrumentsName`,`Time`),
  KEY `InstrumentsName_Time_idx` (`InstrumentsName`,`Time`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT '合约详表';

delete from Instrument_info where InstrumentsName="TF";
delete from Instrument_details where InstrumentsName="TF";
delete from Future_redetails where InstrumentsName="TF" or InstrumentsName="TF";

INSERT INTO Instrument_info (InstrumentsName,Exchange) VALUES("TF","hq_cffex_k1");
INSERT INTO Instrument_info (InstrumentsName,Exchange) VALUES("CF","hq_czce_k1");
#TF1406 1406131515 以后无数据
INSERT INTO Instrument_details  (InstrumentsName,Period,BeginTime) VALUES("TF","1406","140604");
#INSERT INTO Instrument_details  (InstrumentsName,Period,BeginTime) VALUES("TF","1409","140626");
#CF1407 1406012
INSERT INTO Instrument_details  (InstrumentsName,Period,BeginTime) VALUES("CF","1407","140610");
INSERT INTO Instrument_details  (InstrumentsName,Period,BeginTime) VALUES("CF","1409","140615");
#INSERT INTO Instrument_details  (InstrumentsName,Period,BeginTime) VALUES("CF","1411","140618");
