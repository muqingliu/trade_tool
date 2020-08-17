<?php

require_once "common/connInfo.php";
require_once "common/db.php";
require_once "common/common.php";
require_once "common/common_trade.php";
require_once "common/CPosition.php";
require_once "common/common_stock.php";

$db = CreateDatabase();
if(!$db){
    return;
}

$db_price = CreateDatabaseData();
if(!$db_price){
    return;
}

$DEFAULT_BEGIN_DATE = 20050101;
$UPDATE_DB_DAYS = 7;
$SQL_LOG = 0;
if (file_exists("system.ini")) {
    $sys_ini_array = parse_ini_file("system.ini", true);
    if (null == $sys_ini_array) {
        write_log("error", "文件[".$_REQUEST["f"]."] 配置文件[system.ini]解析失败");
        return;
    }
    $DEFAULT_BEGIN_DATE = $sys_ini_array["main"]["default_begin_time"];
    $UPDATE_DB_DAYS = $sys_ini_array["main"]["update_db_days"];
    $SQL_LOG = $sys_ini_array["main"]["sql_log"];
}

function is_mask_in_param($param, $key)
{
    $count = strlen($param);
    for ($i=0; $i<$count; $i++) {
        $param_key = $param[$i];
        if ($param_key == $key) {
            return TRUE;
        }
    }

    return FALSE;
}

function backtest_trading($db, $trading_days, $datas, $output_param, $houseware, $limit_day_num, &$log){
    $posMgr = new CPositionsManager(true, true, $houseware);
    
    $data_keys = array_keys($datas);
    $data_key_count = count($data_keys);
    $begin_date = $data_key_count > 0 ? $data_keys[0] : $DEFAULT_BEGIN_DATE;
    $index = 0;
    $day_profits = null;
    $contract_day_profit = array();
    $day_log = array();
    $contract_diviend = array();
    $contract_last_price = array(); // 记录停牌前最后的价格
    $contract_ave_price = array();
    $contract_last_pos_profit = array();
    $contract_last_open_price = array();
    $contract_volume = array();
    foreach($trading_days as $date){
        $data_end = FALSE;
        if ($index >= $data_key_count) {
            $data_end = TRUE;
        }

        $loop_count = 0;
        while (TRUE) {
            if($index >= $data_key_count){
                break;
            }

            $data_key = $data_keys[$index];
            if($data_key > $date){
                break;
            }

            if(!is_array($day_profits)) {
                $day_profits = array();
            }
            
            $date_datas = $datas[$data_key];
            foreach ($date_datas as $data) {
                // 模拟交易
                $contract =  makeStockID($data["stock_id"]);
                $stock_name = $data["stock_name"];
                $amount = abs($data["amount"]);
                $price = $data["price"];
                $money1 = array_key_exists("money1", $data) ? $data["money1"] : 0;
                $money2 = array_key_exists("money2", $data) ? $data["money2"] : 0;
                $money = $money2 != 0 ? $money2 : $money1;
                $commission = array_key_exists( "commission", $data) ? $data["commission"] : 0;
                $exchange_fee = array_key_exists( "exchange_fee", $data) ? $data["exchange_fee"] : 0;
                $stamps_tax = array_key_exists( "stamps_tax", $data) ? $data["stamps_tax"] : 0;
                $transfer_fee = array_key_exists( "transfer_fee", $data) ? $data["transfer_fee"] : 0;
                $stock_trading_fees = array_key_exists( "stock_trading_fees", $data) ? $data["stock_trading_fees"] : 0;
                $total_commission = $commission+$stamps_tax+$transfer_fee+$stock_trading_fees+$exchange_fee;
                switch($data["type"]){
                    case "buy":
                        $posMgr->open($data_key, $contract, 0, $amount, $price, $total_commission);
                        break;
                    case "sell":
                        $profit = $posMgr->close($data_key, $contract, 1, $amount, $price, $total_commission, false, $log);
                        break;
                    case "dividend": // 分红
                        $posMgr->diviend($contract, $data_key, $money);
                        break;
                    case "allotment": // 配股
                        $posMgr->allotment($contract, $data_key, $amount);
                        break;
                    case "securities_lending": // 融券
                        if ($money2 != 0) {
                            $posMgr->SecuritiesLending($contract, abs($money2), 0);
                        }
                        else {
                            $posMgr->SecuritiesLending($contract, $money1 + $total_commission, $total_commission);
			}
                        break;
                    case "securities_repurchase": //融券购回
                        if ($money2 != 0) {
                            $posMgr->SecuritiesRepurchase($contract, abs($money2), 0);
                        }
                        else {
                            $posMgr->SecuritiesRepurchase($contract, $money1 - $total_commission, $total_commission);
                        }
                        break;
                    case "margin_buy": // 保证金产品申购
                        $posMgr->margin_buy($contract, $amount, $total_commission);
                        break;
                    case "margin_redeem": // 保证金产品赎回
                        $posMgr->margin_redeem($contract, $amount, $total_commission);
                        break;
                    case "Interest": // 利息
                        $posMgr->Interest($money);
                        break;
                    case "tax": // 税
                        $posMgr->pay_tax($contract, $money);
                        break;
                }
            }
            
            // 索引顺加
            $index++;
            $loop_count++;
            if($loop_count > 100000){ // 循环保护
                break;
            }
        }
        
        $posMgr->increase_day_counter();
        // 计算每日净值
        if(is_array($day_profits)){
            if ($data_end) {
                $posMgr->ex_right_price($db, $date);
            }
            $contracts = $posMgr->get_contracts();

            $prices = get_stock_price($db, $contracts, $date);
            foreach($prices as $c => $p){
                $contract_last_price[$c] = $p;
            }

            $day_profit = $posMgr->get_position_profit($contract_last_price, $date) + $posMgr->get_profit();
            $day_profits[$date] = $day_profit;

            foreach ($contracts as $contract) {
                if (array_key_exists($contract, $contract_last_price)) {
                    $price = $contract_last_price[$contract];
                    $contract_day_profit[$date][$contract] = $posMgr->get_contract_position_profit($contract, $price) + $posMgr->get_profit($contract);
                }
                else {
                    $contract_day_profit[$date][$contract] = $posMgr->get_profit($contract);
                }
            }
            
            // 在每日盈亏中加入利息
            $lx_profit = $posMgr->get_profit("lx");
            if ($lx_profit != 0) {
                $contract_day_profit[$date]["lx"] = $posMgr->get_profit("lx");
            }
        }
    }

    if ($limit_day_num > 0) {
        $limit_contract_day_profit = array();
        $limit_day_profits = array();
        $limit_trading_days = array();
        $trading_day_len = count($trading_days);
        for ($i = $trading_day_len - 1; $i>=$trading_day_len - $limit_day_num && $i>=0; $i--) {
            $trading_day = $trading_days[$i];
            array_unshift($limit_trading_days, $trading_day);
        }

        foreach ($limit_trading_days as $limit_trading_day) {
            $limit_day_profits[$limit_trading_day] = $day_profits[$limit_trading_day];
            $limit_contract_day_profit[$limit_trading_day] = $contract_day_profit[$limit_trading_day];
        }

        $result["contract_day_profit"] = $limit_contract_day_profit;
        $result["day_profit"] = $limit_day_profits;
    }
    else {
        $result["contract_day_profit"] = $contract_day_profit;
        $result["day_profit"] = $day_profits;
    }
    
    return $result;
}


function merge_stock_datas(&$new_datas, $datas, $head)
{
    foreach ($datas as $data) {
        $new_data = array();
        
        foreach ($head as $key => $value) {
            if (array_key_exists($value, $data)) {
                $new_data[$key] = $data[$value];
            }
        }
        
        $date = $new_data["date"];
        if (array_key_exists($date, $new_datas)) {
            $new_datas[$date][] = $new_data;
        }
        else {
            $new_datas[$date] = array();
            $new_datas[$date][] = $new_data;
        }
    }
    
    return $new_datas;
}

function flush_equity(){
    global $db;
    global $db_price;
    global $DEFAULT_BEGIN_DATE;
    global $UPDATE_DB_DAYS;
    global $SQL_LOG;
    
    if(!is_readable("log")){
        mkdir('log');
    }
    try{
        // 在界面上显示日志
        $log_set = array();
        $log_set["pos"] = array();
        $log_set["config"] = array();
        $log_set["other"] = array();

        $account_id = "";
        $filenames = array();
        $handle = opendir("res/db");
        if($handle) {
            while(($fl = readdir($handle)) !== false) {
                if($fl == '.' || $fl == '..') {
                    continue;
                }
                else {
                    $index = strpos($fl, ".");
                    $ext = substr($fl, $index+1);
                    if (strcmp($ext, "xls") == 0 || strcmp($ext, "csv") == 0 || strcmp($ext, "xlsx") == 0) {
                        $filenames[] = sprintf("res/db/%s", $fl);
                    }
                    else if (strcmp($ext, "account") == 0) {
                        $account_id = substr($fl, 0, $index);
                    }
                }
            }
        }

        // // 获取交易记录数据
        // $filenames = array();
        // for ($i=0; $i < 100; $i++) { 
        //     $filename = sprintf('res/db/table%u.xls', $i+1);
        //     if (file_exists($filename)) {
        //         $filenames[] = $filename;
        //     }
        //     else {
        //         break;
        //     }
        // }

        $inout_money = 0;
        $new_datas = array();
        $new_stock_names = array();
        foreach ($filenames as $filename) {
            $filename = iconv('UTF-8', 'GB2312', $filename);
            $datas = parse_cvs($filename, $log_set);
            if (null == $datas) {
                return null;
            }

            // 获取头部的索引号
            $filename_utf8 = iconv('GB2312', 'UTF-8', $filename);
            $head = get_data_head($filename_utf8, $datas, $log_set);
            if (null == $head) {
                return null;
            }

            if (0 == $inout_money) {
               $inout_money = get_inout_money($db, $account_id);
            }
            $stock_names = get_stock_names($head, $datas);
            foreach ($stock_names as $key => $value) {
                if (!array_key_exists($key, $new_stock_names)) {
                    $new_stock_names[$key] = $value;
                }
            }
            
            merge_stock_datas($new_datas, $datas, $head);
        }

        ksort($new_datas);

        $trading_days = get_trading_day($db_price, $UPDATE_DB_DAYS);
        $data_result = backtest_trading($db_price, $trading_days, $new_datas, '*', $filename_utf8, $UPDATE_DB_DAYS, $log_set);
        
        $day_profit = $data_result["day_profit"];
        $contract_day_profit = $data_result["contract_day_profit"];

        if ($SQL_LOG == 1) {
            foreach($day_profit as $date=>$profit){
                if(isset($contract_day_profit[$date])){
                    $contract_profit = $contract_day_profit[$date];
                    foreach($contract_profit as $C => $P) {
                        $sql = "replace into fd_report_profit values('$account_id',$date,'$C',$P,'',0)";
                        write_log($account_id."_sql", $sql);
                    }
                }
            }
        }
        else {
            $db->executesql("begin transaction");
            foreach($day_profit as $date=>$profit){
                if(isset($contract_day_profit[$date])){
                    $contract_profit = $contract_day_profit[$date];
                    foreach($contract_profit as $C => $P) {
                        $sql = "replace into fd_report_profit values('$account_id',$date,'$C',$P,'',0)";
                        $result = $db->executesql($sql);
                    }
                }
            }
            $db->executesql("commit transaction");
        }
    }
    catch (Exception $e){
        write_log("error", "文件[".$_REQUEST["f"]."] ".$e->getMessage());
    }
}

flush_equity();

?>

            