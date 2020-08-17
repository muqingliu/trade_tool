<?php

require_once "connInfo.php";
require_once "db.php";
require_once "common.php";
require_once "common_trade.php";
require_once "CPosition.php";

function _fgetcsv(& $handle, $length = null, $d = ',', $e = '"') {
     $d = preg_quote($d);
     $e = preg_quote($e);
     $_line = "";
     $eof=false;
     while ($eof != true) {
         $_line .= (empty ($length) ? fgets($handle) : fgets($handle, $length));
         $itemcnt = preg_match_all('/' . $e . '/', $_line, $dummy);
         if ($itemcnt % 2 == 0)
             $eof = true;
     }
     $_csv_line = preg_replace('/(?: |[ ])?$/', $d, trim($_line));
     $_csv_pattern = '/(' . $e . '[^' . $e . ']*(?:' . $e . $e . '[^' . $e . ']*)*' . $e . '|[^' . $d . ']*)' . $d . '/';
     preg_match_all($_csv_pattern, $_csv_line, $_csv_matches);
     $_csv_data = $_csv_matches[1];
     for ($_csv_i = 0; $_csv_i < count($_csv_data); $_csv_i++) {
         $_csv_data[$_csv_i] = preg_replace('/^' . $e . '(.*)' . $e . '$/s', '$1' , $_csv_data[$_csv_i]);
         $_csv_data[$_csv_i] = str_replace($e . $e, $e, $_csv_data[$_csv_i]);
     }
     return empty ($_line) ? false : $_csv_data;
}

function parse_cvs($filename, &$log)
{
    $handle = fopen($filename,"r");
    if(null == $handle) {
        $filename_utf8 = iconv('GB2312', 'UTF-8', $filename);
        $log["config"][] = sprintf("交易记录文件[%s]不存在", $filename_utf8);
        write_log("error", sprintf("交易记录文件[%s]不存在", $filename_utf8));
        return null;
    }

    $line = 0;
    $datas = array();
    while ($data = _fgetcsv ($handle,100000,"\n")) { //循环表的所有行
        for ($i = 0; $i < count($data); $i++) { //I=0开始，为一行中的第一列内容，以下是循环输出一行的各列内容
            $value = $data[$i];

            $value = iconv('gbk','utf-8', $value);

            $comma_pos = strpos($value, ","); // 如果是逗号分隔
            if($comma_pos !==false){
                $value = preg_replace("#,,#", ",0,", preg_replace("#,,#", ",0,", $value, -1), -1); // 替换两次才能把两个,中间都替换掉
                $e = preg_split("#,#", $value, -1, PREG_SPLIT_NO_EMPTY);
            }
            else{
                $value = preg_replace("#\t\t#", "\t0\t", preg_replace("#\t\t#", "\t0\t", $value, -1), -1); // 替换两次才能把两个\t中间都替换掉
                $e = preg_split("#\s+#", $value, -1, PREG_SPLIT_NO_EMPTY);
            }

            if(count($e)>0 && strlen($e[0]) > 1){
                $datas[] = $e;
            }
            $line ++;
        }
    }
    return $datas;
}


function makeStockID($id){
    return sprintf(strlen($id) == 6 && ($id[0] == '6' || $id[0] == '5') ? "sh%06d" : "sz%06d", intval($id));
}

function getStockID($head, $csv_datas){
    $keys = array();
    foreach($csv_datas as $data){
        $sid =$data[$head["stock_id"]];
        if(intval($sid)>0){
            $keys[] = makeStockID($sid);
        }
    }
    $keys = array_unique($keys);
    return $keys;
}

function get_trading_day($db){
    $sql = sprintf("SELECT * FROM %s WHERE id = 'sh000001' ORDER BY time ASC", $GLOBALS['DB_TABLE_DAY_DATA']);
    $recs = $db->executesql($sql);

    $days = array();
    foreach($recs as $r){
        $days[] = $r["time"];
    }

    return $days;
}

function get_ex_right_price($db, $contract, $begin_date, $datetime, $price){
    $sql = sprintf("SELECT * FROM %s WHERE id='%s' and date>='%s' and date<='%s' ORDER BY date", $GLOBALS['DB_TABLE_DIVIDEND_ALLOTMENT'], $contract, $begin_date, $datetime);
    $recs = $db->executesql($sql);

    $ex_right_price = $price;
    foreach ($recs as $rec) {
        $transfer = $rec['transfer'];
        $qty = $rec['qty'];
        $divided_price = $rec['price'];
        $dividend = $rec['dividend'];
        $ex_right_price = $ex_right_price*(1+$transfer/10.0 + $qty/10.0) - $qty/10.0*$divided_price + $dividend*0.9/10.0;
    }

    return $ex_right_price;
}

function get_ex_right_prices($db, &$contract_prices, $begin_date, $datetime)
{
    $contracts = array_keys($contract_prices);
    $sql = sprintf("SELECT * FROM %s WHERE id in (%s) and date>='%s' and date<='%s' ORDER BY date", $GLOBALS['DB_TABLE_DIVIDEND_ALLOTMENT'], "'".str_replace(",","','",join(",",$contracts))."'", $begin_date, $datetime);
    $recs_dividend = $db->executesql($sql);

    $contract_dividend = array();
    foreach($recs_dividend as $rec_dividend){
        $contract = $rec_dividend['id'];
        $price = $contract_prices[$contract];
        $transfer = $rec_dividend['transfer'];
        $qty = $rec_dividend['qty'];
        $divided_price = $rec_dividend['price'];
        $dividend = $rec_dividend['dividend'];
        $contract_prices[$contract] = $price *(1+$transfer/10.0 + $qty/10.0) - $qty/10.0*$divided_price + $dividend*0.9/10.0;
    }
}

function get_stock_open_price($db, $stock_ids, $datetime){
    $sql = sprintf("SELECT id, open FROM %s WHERE id in (%s) and time='%s'", $GLOBALS['DB_TABLE_DAY_DATA'], "'".str_replace(",","','",join(",",$stock_ids))."'", $datetime);
    $recs = $db->executesql($sql);

    $contract_open_prices = array();
    foreach($recs as $rec){
        $contract_open_prices[$rec["id"]] = $rec["open"];
    }
    return $contract_open_prices;
}

function get_stock_price($db, $stock_ids, $datetime){
    $sql = sprintf("SELECT id, close FROM %s WHERE id in (%s) and time='%s'", $GLOBALS['DB_TABLE_DAY_DATA'], "'".str_replace(",","','",join(",",$stock_ids))."'", $datetime);
    $recs = $db->executesql($sql);

    $contract_prices = array();
    foreach($recs as $rec){
        $contract_prices[$rec["id"]] = $rec["close"];
    }
    return $contract_prices;
}

function fix_query_date($date){
    $next_days = 0;
    if(date("w") == 6){
        $next_days = -1;
    }
    elseif(date("w") == 0) {
        $next_days = -2;
    }
    if($next_days !=0){
        $date = get_next_day($date, $next_days);
    }
    return $date;
}

// 补充K线数据
function supply_stock_k_data($filename, $db, $stock_ids, $default_begin_time, &$log){
    $last_new_tradingday = fix_query_date(date("Ymd"));
    $count = 0;
    while (count($stock_ids) > 0) {
        $err_stock_ids = array();
        foreach($stock_ids as $id){
            $query_stock_id = $id;
            $sql = sprintf("SELECT * FROM %s WHERE id = '%s' ORDER BY time DESC LIMIT 1", $GLOBALS['DB_TABLE_DAY_DATA'], $query_stock_id);
            $recs = $db->executesql($sql);
            $begin_date = $default_begin_time;

            if(isset($recs) && count($recs) > 0){
                $begin_date = $recs[0]["time"];
                $begin_date = get_next_day($begin_date);
            }

            if($begin_date <= $last_new_tradingday){       
                try{
                    $query_url = sprintf("http://biz.finance.sina.com.cn/stock/flash_hq/kline_data.php?symbol=%s&end_date=%d&begin_date=%d", 
                        $query_stock_id, $last_new_tradingday, $begin_date);

                    $xml_kdatas = httpPost($query_url, null);
            	    $xml = simplexml_load_string($xml_kdatas);
            	    $datas = json_decode(json_encode($xml),TRUE);

                    if(!$datas){
                        $err_stock_ids[] = $id;
                    }
                    elseif(array_key_exists("content", $datas)){
                        $number = count($datas["content"]);
                        
                        $db->executesql("begin transaction");
                        for($i = 0; $i< $number; $i++){
                            $day_keyline = null;
                            if($number == 1){
                                $day_keyline = $datas["content"]["@attributes"]; // 如果只有一个元素，数组结构是不同的
                            }
                            else{
                                $day_keyline = $datas["content"][$i]["@attributes"];
                            }

                            $sql = sprintf("INSERT INTO %s VALUES('%s', '%s', %s, %s, %s, %s, %s, 0)", $GLOBALS['DB_TABLE_DAY_DATA'], 
                                $query_stock_id, str_replace('-','',$day_keyline["d"]), $day_keyline["o"], $day_keyline["h"], 
                                $day_keyline["l"], $day_keyline["c"], $day_keyline["v"]);
                            $db->executesql($sql);
                        }
                        $db->executesql("commit transaction");
                    }
                }
                catch (Exception $e)
                {
                    $log["other"][] = "文件[".$filename."] ".$e->getMessage();
                    write_log("error", "文件[".$filename."] ".$e->getMessage());
                    $err_stock_ids[] = $id;
                }
            }
        }

        if (count($err_stock_ids) > 0) {
            $log_str = sprintf("文件[%s] 第%u次重请求:", $filename, $count + 1);
            foreach ($err_stock_ids as $id) {
                $log_str.sprintf("%s ", $id);
            }
            write_log("repeat", $log_str);
            $log["other"][] = $log_str;
        }
        $stock_ids = $err_stock_ids;

        $count++;
        if ($count >= 10) {
            break;
        } 
    }
}

function get_data_head($filename, &$datas, &$log){
    $ini_array = parse_head_type_ini($filename);
    if(null == $ini_array){
        return null;
    }

    $head_ini_array = $ini_array["header"];
    $type_ini_array = $ini_array["type"];
    $type_keys = array_keys($type_ini_array);
    $critical_ini_array = $ini_array["critical"];

    $r_data = array();
    $head = null;
    foreach($datas as $value){
        if($head == null){
            $head = $value;
        }
        else{
            $r_data[] = $value;
        }
    }

    $head_rtn = array();
    foreach($head as $index=>$key_name){
        $index_name = null;
        if (array_key_exists($key_name, $head_ini_array)) {
            $index_name = $head_ini_array[$key_name];
        }
        else {
            $log["config"][] = "文件[".$filename."][header]中关键字[".$key_name."]未被配置";
            write_log("error", "文件[".$filename."][header]中关键字[".$key_name."]未被配置");
        }

        if($index_name != null){
            $head_rtn[$index_name] = $index;
        }
    }
    $datas = $r_data;
    
    foreach ($critical_ini_array as $key => $value) {
        if (!array_key_exists($key, $head_rtn)) {
            write_log("error", "文件[".$filename."]中critical关键字[".$key."]未被配置");
        }
    }

    for($idx =0; $idx < count($datas); $idx++){
        $data = &$datas[$idx];
        if (strstr($data[$head_rtn["type"]], "(") != null && strstr($data[$head_rtn["type"]], ")") != null) {
            $data[$head_rtn["type"]] = substr($data[$head_rtn["type"]], 0, strrpos($data[$head_rtn["type"]],"("));
        }
        
        $is_find = FALSE;
        foreach ($type_keys as $type_key) {
            if (strcmp($data[$head_rtn["type"]], $type_key) == 0) {
                $data[$head_rtn["type"]] = $type_ini_array[$type_key];
                // if ($type_ini_array[$type_key] == "Interest") {
                //     write_log("content", "名称:".$type_key." 对应关键字:".$data[$head_rtn["type"]]);                    
                // }

                $is_find = TRUE;
                break;
            }
        }
        
        if (!$is_find) {
            $log["config"][] = "文件[".$filename."][type]中关键字[".$data[$head_rtn["type"]]."]未被配置";
            write_log("error", "文件[".$filename."][type]中关键字[".$data[$head_rtn["type"]]."]未被配置");
        }
    }

    return $head_rtn;
}

function get_user_id($head, $datas){
    $user_id = "";
    foreach ($datas as $data) {
        $user_id = $data[$head["user_id"]];
        if (strlen($user_id) > 0) {
            break;
        }
    }
    return $user_id;
}

function get_stock_names($head, $datas){
    $names = array();
    foreach($datas as $data){
        $stock_id = makeStockID($data[$head["stock_id"]]);
        if (!array_key_exists($stock_id, $names) || strlen($names[$stock_id]) == 0) {
            $names[$stock_id] = $data[$head["stock_name"]];            
        }
    }
    return $names;
}

function get_latest_day($accountID, $db, $default_begin_time){
    $sql = "select max(`time`) as time from fd_report_profit where accountID='$accountID'";
    $recs = $db->executesql($sql);
    if (null == $recs || count($recs) == 0) {
        return 0;
    }
    return intval($recs[0]['time']);
}

function parse_head_type_ini($filename){
    $ret = array();
    $ini_array = parse_ini_file("head_type.ini", true);
    if (null == $ini_array) {
        write_log("error", "文件[".$filename."] 配置文件[head_type.ini]解析失败");
        return null;
    }

    foreach ($ini_array as $sec_key => $ini_sec_array) {
        $ret_sec = array();
        foreach ($ini_sec_array as $key => $value_conn_str) {
            $value_array = explode("|", $value_conn_str);
            foreach ($value_array as $value) {
                $ret_sec[$value] = $key;
            }
        }
        $ret[$sec_key] = $ret_sec;
    }
    
    return $ret;
}

function sort_log(&$log_items, &$log_count, $log_set)
{
    foreach ($log_set["pos"] as $value) {
        $log_row = array();
        $log_row["log"] = $value;
        array_push($log_items, $log_row);
        $log_count++;
    }
    foreach ($log_set["config"] as $value) {
        $log_row = array();
        $log_row["log"] = $value;
        array_push($log_items, $log_row);
        $log_count++;
    }
    foreach ($log_set["other"] as $value) {
        $log_row = array();
        $log_row["log"] = $value;
        array_push($log_items, $log_row);
        $log_count++;
    }
}
?>


