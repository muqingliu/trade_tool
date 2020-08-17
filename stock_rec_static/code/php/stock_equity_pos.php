<?php

require_once "common/connInfo.php";
require_once "common/db.php";
require_once "common/common.php";
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
if (file_exists("system.ini")) {
    $sys_ini_array = parse_ini_file("system.ini", true);
    if (null == $sys_ini_array) {
        write_log("error", "文件[".$_REQUEST["f"]."] 配置文件[system.ini]解析失败");
        return;
    }
    $DEFAULT_BEGIN_DATE = $sys_ini_array["main"]["default_begin_time"];
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

function backtest_trading($db, $trading_days, $head, $datas, $output_param, $houseware, &$log){
    $posMgr = new CPositionsManager(true, true, $houseware);

    $data_count = count($datas);
    $begin_date = $data_count > 0 ? $datas[0][$head["date"]] : $DEFAULT_BEGIN_DATE;
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
    $last_pos_contracts = array();
    foreach($trading_days as $date){
        $data_end = FALSE;
        if ($index >= $data_count) {
            $data_end = TRUE;
        }

        $loop_count = 0;
        while (TRUE) {
            if($index >= $data_count){
                break;
            }

            $data = $datas[$index];
            $datetime = $data[$head["date"]];
            if($datetime > $date){
                break;
            }

            if(!is_array($day_profits)) {
                $day_profits = array();
            }

            // 模拟交易
            $contract =  makeStockID($data[$head["stock_id"]]);
            $stock_name = $data[$head["stock_name"]];
            $amount = abs($data[$head["amount"]]);
            $price = $data[$head["price"]];
            $money1 = array_key_exists( "money1", $head) ? $data[$head["money1"]] : 0;
	    $money2 = array_key_exists( "money2", $head) ? $data[$head["money2"]] : 0;
            $money = $money2 != 0 ? $money2 : $money1;
            $commission = array_key_exists( "commission", $head) ? $data[$head["commission"]] : 0;
            $exchange_fee = array_key_exists( "exchange_fee", $head) ? $data[$head["exchange_fee"]] : 0;
            $stamps_tax = array_key_exists( "stamps_tax", $head) ? $data[$head["stamps_tax"]] : 0;
            $transfer_fee = array_key_exists( "transfer_fee", $head) ? $data[$head["transfer_fee"]] : 0;
            $stock_trading_fees = array_key_exists( "stock_trading_fees", $head) ? $data[$head["stock_trading_fees"]] : 0;
            $total_commission = $commission+$stamps_tax+$transfer_fee+$stock_trading_fees+$exchange_fee;
            switch($data[$head["type"]]){
                case "buy":
                    $posMgr->open($datetime, $contract, 0, $amount, $price, $total_commission);
                    $day_log[$date][] = sprintf("证券买入：%s %d 股，手续费 %d", $stock_name, $amount, $total_commission);
                    break;
                case "sell":
                    $profit = $posMgr->close($datetime, $contract, 1, $amount, $price, $total_commission, false, $log);
                    $day_log[$date][] = sprintf("证券卖出：%s %d 股,获利 %d", $stock_name, $amount, $profit);
                    break;
                 case "dividend": // 分红
                    $posMgr->diviend($contract, $datetime, $money);
                    $day_log[$date][] = sprintf("分红：%s %d", $stock_name, $money);
                    break;
                case "allotment": // 配股
                    $posMgr->allotment($contract, $datetime, $amount);
                    $day_log[$date][] = sprintf("配股：%s %d", $stock_name, $amount);
                    break;
                case "securities_lending": // 融券
	            if ($money2 != 0) {
	            	$posMgr->SecuritiesLending($contract, abs($money2), 0);
	                $day_log[$date][] = sprintf("融券：合约[%s] %d", $contract, abs($money2));
	            }
	            else {
	            	$posMgr->SecuritiesLending($contract, $money1 + $total_commission, $total_commission);
	                $day_log[$date][] = sprintf("融券：合约[%s] %d", $contract, $money1 + $total_commission);
	            }
                    break;
                case "securities_repurchase": //融券购回
                    if ($money2 != 0) {
                    	$posMgr->SecuritiesRepurchase($contract, abs($money2), 0);
                        $day_log[$date][] = sprintf("融券购回：合约[%s] %d", $contract, abs($money2));
                    }
                    else {
                    	$posMgr->SecuritiesRepurchase($contract, $money1 - $total_commission, $total_commission);
                        $day_log[$date][] = sprintf("融券购回：合约[%s] %d", $contract, $money1 - $total_commission);
                    }
                    break;
                case "margin_buy": // 保证金产品申购
                    $posMgr->margin_buy($contract, $amount, $total_commission);
                    $day_log[$date][] = sprintf("保证金产品申购：合约[%s] %d", $contract, $amount);
                    break;
                case "margin_redeem": // 保证金产品赎回
                    $posMgr->margin_redeem($contract, $amount, $total_commission);
                    $day_log[$date][] = sprintf("保证金产品赎回：合约[%s] %d", $contract, $amount);
                    break;
                case "Interest": // 利息
                    $posMgr->Interest($money);
                    $day_log[$date][] = sprintf("利息：%d", $money);
                     break;
                case "tax": // 税
                    $posMgr->pay_tax($contract, $money);
                    $day_log[$date][] = sprintf("税：%s %d", $stock_name, $money);
                    break;
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
            $contracts = $posMgr->get_contracts(); // 获取持仓的股票
            $pos_contracts = $posMgr->get_pos_contracts();

            $prices = get_stock_price($db, $contracts, $date);
            $open_prices = get_stock_open_price($db, $contracts, $date);
            foreach($prices as $c => $p){
                $contract_last_price[$c] = $p;
                $contract_last_open_price[$c] = $open_prices[$c];
            }

            $contract_ave_price = $posMgr->get_contract_ave_price(0);

            if (count($last_pos_contracts) > 0 || count($pos_contracts) > 0) {
                $day_profit = $posMgr->get_position_profit($contract_last_price, $date) + $posMgr->get_profit();
                $day_profits[$date] = $day_profit;   
            }
            
            foreach ($contracts as $contract) {
                if (array_key_exists($contract, $contract_last_price)) {
                    $price = $contract_last_price[$contract];
                    if (in_array($contract, $pos_contracts) || in_array($contract, $last_pos_contracts)) {
                        $contract_day_profit[$date][$contract] = $posMgr->get_contract_position_profit($contract, $price) + $posMgr->get_profit($contract);
                    }
                    $contract_last_pos_profit[$contract] = $posMgr->get_contract_position_profit($contract, $price);
                }
                else {
                    if (in_array($contract, $pos_contracts) || in_array($contract, $last_pos_contracts)) {
                        $contract_day_profit[$date][$contract] = $posMgr->get_profit($contract);
                    }
                }
                $contract_day_counter[$contract] = $posMgr->get_stock_day_counter($contract);
                $volumes = $posMgr->get_volume($contract);
                $contract_volume[$contract] = $volumes[0];
                $contract_diviend[$contract] = $posMgr->get_diviend($contract);
            }
            
            // 在每日盈亏中加入利息
            $lx_profit = $posMgr->get_profit("lx");
            if ($lx_profit != 0) {
                $contract_day_profit[$date]["lx"] = $posMgr->get_profit("lx");
            }
            
            $last_pos_contracts = $pos_contracts;
        }
    }

    $total_diviend = 0;
    foreach ($contract_diviend as $contract => $diviend) {
        $total_diviend += $diviend;
    }

    if (is_mask_in_param($output_param, '*')) {
        $result["contract_volume"] = $contract_volume;
        $result['contract_last_open_price'] = $contract_last_open_price;
        $result["contract_last_price"] = $contract_last_price;
        $result["contract_ave_price"] = $contract_ave_price;
        $result["contract_last_pos_profit"] = $contract_last_pos_profit;
        $result["contract_day_profit"] = $contract_day_profit;
        $result["last_commission"] = $posMgr->get_commission();
        $result["diviend"] = $total_diviend;
        $result["contract_diviend"] = $contract_diviend;
        $result["last_profit"] = $posMgr->get_profit();
        $result["day_profit"] = $day_profits;
        $result["day_log"] = $day_log;
    }
    if (is_mask_in_param($output_param, 'm')) {
        $result["last_commission"] = $posMgr->get_commission();
    }
    if (is_mask_in_param($output_param, 'n')) {
        $result["contract_day_profit"] = $contract_day_profit;
        $result["day_profit"] = $day_profits;
    }
    if (is_mask_in_param($output_param, 'p')) {
        $result["contract_volume"] = $contract_volume;
        $result['contract_last_open_price'] = $contract_last_open_price;
        $result["contract_last_price"] = $contract_last_price;
        $result["contract_ave_price"] = $contract_ave_price;
        $result["contract_last_pos_profit"] = $contract_last_pos_profit;
    }
    if (is_mask_in_param($output_param, 'd')) {
        $result["diviend"] = $total_diviend;
        $result["contract_diviend"] = $contract_diviend;
    }
    if (is_mask_in_param($output_param, 'c')) {
        $result['contract_last_open_price'] = $contract_last_open_price;
        $result["contract_last_price"] = $contract_last_price;
    }
    if (is_mask_in_param($output_param, 'f')) {
        $result["contract_last_pos_profit"] = $contract_last_pos_profit;
    }
    if (is_mask_in_param($output_param, 'b')) {
        $result["contract_ave_price"] = $contract_ave_price;
    }

    return $result;
}

function get_account_info($user_id, $inout_money, $data_result)
{
    $contract_ave_price = $data_result["contract_ave_price"];
    $contract_volume = $data_result["contract_volume"];
    $contract_last_pos_profit = $data_result["contract_last_pos_profit"];
    $total_profit = $data_result["last_profit"];
    $total_float_profit = 0;
    $total_market_value = 0;
    foreach ($contract_ave_price as $contract => $average) {
        $floatProfit = array_key_exists($contract, $contract_last_pos_profit) ? $contract_last_pos_profit[$contract] : 0;
        $total_float_profit += $floatProfit;
        $volume = $contract_volume[$contract];
        $marekt_value = $average * $volume + $floatProfit;
        $total_market_value += $marekt_value;
    }
    $available_money = $inout_money + $total_profit - $total_market_value + $total_float_profit;
    $total_funds = $available_money + $total_market_value;

    $account_info = array();
    $account_info["user_id"] = $user_id;
    $account_info["money"] = sprintf("资产总额:%.2f &nbsp;可用资金:%.2f &nbsp;出入金:%.2f &nbsp;总盈亏:%.2f &nbsp;市值:%.2f", $total_funds,
            $available_money, $inout_money, $total_profit + $total_float_profit, $total_market_value);

    return $account_info;
}

function get_account_warn($db, $user_id)
{
    $sql = sprintf("select * from %s where account_id='%s'", $GLOBALS['DB_TABLE_ACCOUNT_WARN'], $user_id);
    $recs = $db->executesql($sql);
    if (null == $recs || count($recs) == 0) {
        return null;
    }

    $account_warn = array();
    $account_warn['warn_line'] = $recs[0]['warn_line'];
    $account_warn['close_line'] = $recs[0]['close_line'];

    return $account_warn;
}

function get_contract_table_res($stock_names, $data_result)
{
    $contract_volume = $data_result["contract_volume"];
    $contract_last_open_price = $data_result["contract_last_open_price"];
    $contract_last_price = $data_result["contract_last_price"];
    $contract_ave_price = $data_result["contract_ave_price"];
    $contract_last_pos_profit = $data_result["contract_last_pos_profit"];
    $total_float_profit = 0;
    $total_market_value = 0;
    $items = array();
    $count = 0;
    foreach ($contract_ave_price as $contract => $average) {
        $row = array();
        $row['open_price'] = array_key_exists($contract, $contract_last_open_price) ? $contract_last_open_price[$contract] : 0;
        $row['contract'] = $contract;
        $row['name'] = $stock_names[$contract];
        $row['volume'] = sprintf("%d", $contract_volume[$contract]);
        $row['ave_price'] = sprintf("%.2f", $average);
        $now_price = array_key_exists($contract, $contract_last_price) ? $contract_last_price[$contract] : 0;
        $row['now_price'] = sprintf("%.2f", $now_price);
        $floatProfit = array_key_exists($contract, $contract_last_pos_profit) ? $contract_last_pos_profit[$contract] : 0;
        $row['floatProfit'] = sprintf("%.2f", $floatProfit);
        $total_float_profit += $floatProfit;
        if (0 != $average) {
            $row['ratio'] = sprintf("%.2f%%", ($now_price - $average) * 100 / $average);
        } 
        $marekt_value = $average * $contract_volume[$contract] + $floatProfit;
        $row['marketValue'] = sprintf("%.2f", $marekt_value);
        $total_market_value += $marekt_value;
        $items[] = $row;
        $count++;
    }

    $footer = array();
    $item_footer['floatProfit'] = sprintf("%.2f", $total_float_profit);
    $item_footer['marketValue'] = sprintf("%.2f", $total_market_value);
    $footer[] = $item_footer;
    $count++;

    $contract_table_res = array();
    $contract_table_res['rows'] = $items;
    $contract_table_res['footer'] = $footer;
    $contract_table_res['total'] = $count;

    return $contract_table_res;
}

function show_calc(){
    global $db;
    global $db_price;
    global $DEFAULT_BEGIN_DATE;
    
    if(!is_readable("log")){
        mkdir('log');
    }
    try{
        // 获取交易记录数据
    	$filename = 'res/db/table1.xls';
    	if(array_key_exists( 'f',$_REQUEST)) {
    		$filename = 'res/db/'.$_REQUEST["f"];
    	}
        $filename = iconv('UTF-8', 'GB2312', $filename);
	
        // 在界面上显示日志
        $log_set = array();
        $log_set["pos"] = array();
        $log_set["config"] = array();
        $log_set["other"] = array();

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

        $user_id = get_user_id($head, $datas);
        $inout_money = get_inout_money($db, $user_id);
        $stock_names = get_stock_names($head, $datas);

        $stock_ids = getStockID($head, $datas);
        $stock_ids[] = "sh000001"; // 大盘指数加入队列，每次补充
        //supply_stock_k_data($filename_utf8, $db_price, $stock_ids, $DEFAULT_BEGIN_DATE, $log_set);
        $trading_days = get_trading_day($db_price);
        $data_result = backtest_trading($db_price, $trading_days, $head, $datas, '*', $filename_utf8, $log_set);
        
        $log_items = array();
        $log_count = 0;
        sort_log($log_items, $log_count, $log_set);
        
        // 获取账号警戒信息
        $account_warn = get_account_warn($db_price, $user_id);
        // 为账号信息输出
        $account_info = get_account_info($user_id, $inout_money, $data_result);
        // 为合约表格输出
        $contract_table_res = get_contract_table_res($stock_names, $data_result);

        // 为净值曲线输出
        $g_max_value = 0;
        $g_min_value = 999999999;
        $times_str ="[";
        $series_str = "[";
        $contract_strs = array();
        $day_profit_str = "";
        $warn_line_str = "";
        $close_line_str = "";
        $day_profit = $data_result["day_profit"];
        $index = 0;
        $total_count = count($day_profit);
        foreach($day_profit as $date=>$profit){
	    $profit = $profit + $inout_money;
	    
            $g_max_value = max($g_max_value, $profit);
            $g_min_value = min($g_min_value, $profit);

            $year = $date/10000;
            $month = $date/100%100-1;
            $day = $date%100;
            $mday = $date%10000;
            // 组织时间轴与总净值
            $times_str .= sprintf("'%d-%04d',", $year, $mday);
            $day_profit_str .= sprintf("[Date.UTC(%d,%d,%d),%.2f],", $year, $month, $day, $profit);

            // 组织各个股票数据
            $contract_day_profit = $data_result["contract_day_profit"];
            if(isset($contract_day_profit[$date])){
                $contract_profit = $contract_day_profit[$date];
                foreach($contract_profit as $C => $P) {
                    if(!array_key_exists($C, $contract_strs)){
                        $contract_strs[$C] = "";
                    }

                    $contract_strs[$C] .= sprintf("[Date.UTC(%d,%d,%d),%.2f],", $year, $month, $day, $P);
                    $g_max_value = max($g_max_value, $P);
                    $g_min_value = min($g_min_value, $P);

                    if (isset($_REQUEST['id'])) {
                        $accountID = $_REQUEST['id'];
                        $lastest_day = get_latest_day($accountID, $db, $DEFAULT_BEGIN_DATE);
                        if ($date > $lastest_day) {
                           $sql = "Insert into fd_report_profit value('$accountID',$date,$C,$P)";
                           $db->executesql($sql);
                        }
                    }
                }
                
                if ($index == 0 || $index == $total_count - 1) {
                    if (null != $account_warn) {
                        $warn_line_str .= sprintf("[Date.UTC(%d,%d,%d),%f],", $year, $month, $day, $account_warn["warn_line"]);
                        $close_line_str .= sprintf("[Date.UTC(%d,%d,%d),%f],", $year, $month, $day, $account_warn["close_line"]);
                        $g_max_value = max($g_max_value, max($account_warn["warn_line"], $account_warn["close_line"]));
                        $g_min_value = min($g_min_value, min($account_warn["warn_line"], $account_warn["close_line"]));    
                    }
                }
            }
            
            $index++;
        }

        $script_day_log = "var day_log={";
        foreach($data_result["day_log"] as $datetime => $logs){
            $script_day_log .= sprintf("'%d%04d': '", $datetime/10000, $datetime%10000);
            $script_day_log .= "<table><tr>";
            $wrap_index = 0;
            foreach($logs as $log){
                $script_day_log.= "<td>".$log."</td>";
                $wrap_index++;
                if ($wrap_index%4 == 0 || $wrap_index == count($logs)) {
                    $script_day_log.="</tr>";
                    if ($wrap_index < count($logs)) {
                        $script_day_log.="<tr>";
                    }
                }
            }
            $script_day_log.= "</table>',";
        }
        $script_day_log .= "};";

        // 组织最终串
        $series_str .= sprintf("{name:'总资产',data:[%s]},", $day_profit_str);
        foreach($contract_strs as $C=>$str){
            if(array_key_exists($C, $stock_names)){
                $series_str .= sprintf("{name:'%s %s',data:[%s]},", $C, $stock_names[($C)], $str);
            }
            else {
                $series_str .= sprintf("{name:'%s',data:[%s]},", $C, $str);
            }
        }
        
        if (null != $account_warn) {
            $series_str .= sprintf("{name:'警戒线',color:'#f7a35c',data:[%s]},", $warn_line_str);
            $series_str .= sprintf("{name:'平仓线',color:'#ff0000',data:[%s]},", $close_line_str);
        }
        $times_str.="]";
        $series_str .="]";

        $script = $script_day_log;
        $script.=
<<<eof
                function tooltip_fun(charts){
                    var daykey=parseInt(Highcharts.dateFormat('%Y%m%d', charts.points[0].x),10);
                    var tip = '<table><tr>';
                    for(var i in charts.points){
                        var chart = charts.points[i];
                        tip += '<td><span style="color:' + chart.series.color + '">\u25CF</span><b>'+ chart.series.name +'</b> ' + Highcharts.dateFormat('%Y-%m-%d', chart.x) + ': '+ chart.y + '</td>';
                        if(i%4 == 0 || i == charts.points.length-1){
                            tip += '</tr>';
                            if(i<charts.points.length-1) tip += '<tr>';
                        }
                    }
                    tip += '</table>';
                    if(day_log[daykey]) tip += day_log[daykey];
                    return tip;
                }
eof;

        $res['account_info'] = $account_info;
        $res['contract_table_res'] = $contract_table_res;
        $res["series"] = $series_str;
        $res["categories"] = $times_str;
        $res["interval"] = ($g_max_value - $g_min_value)/10;
        $res["max_value"] = $g_max_value;
        $res["min_value"] = $g_min_value;
        $res["script"] = $script;
        $res["log_rows"] = $log_items;
        $res["log_count"] = $log_count;
        
        echo json_encode($res);
    }
    catch (Exception $e){
        write_log("error", "文件[".$_REQUEST["f"]."] ".$e->getMessage());
    }
}

show_calc();

?>

            