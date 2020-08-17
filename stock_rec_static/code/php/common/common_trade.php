<?php

//require_once "connInfo.php";
function get_contract_mutil($contract)
{    
    $symbol = preg_replace ('/(\d+)/i', '', $contract);    
    $mul_rate['bu'] = 10;
    $mul_rate['fu'] = 50;
    $mul_rate['hc'] = 10;
    $mul_rate['rb'] = 10;
    $mul_rate['ru'] = 10;
    $mul_rate['wr'] = 10;
    $mul_rate['CF'] = 5;
    $mul_rate['FG'] = 20;
    $mul_rate['JR'] = 20;
    $mul_rate['MA'] = 10;
    $mul_rate['OI'] = 10;
    $mul_rate['PM'] = 50;
    $mul_rate['RI'] = 20;
    $mul_rate['RM'] = 10;
    $mul_rate['RS'] = 10;
    $mul_rate['SR'] = 10;
    $mul_rate['TA'] = 5;
    $mul_rate['TC'] = 100;
    $mul_rate['WH'] = 20;
    $mul_rate['a'] = 10;
    $mul_rate['b'] = 10;
    $mul_rate['bb'] = 500;
    $mul_rate['c'] = 10;
    $mul_rate['fb'] = 500;
    $mul_rate['i'] = 100;
    $mul_rate['j'] = 100;
    $mul_rate['jd'] = 10;
    $mul_rate['jm'] = 60;
    $mul_rate['l'] = 5;
    $mul_rate['m'] = 10;
    $mul_rate['p'] = 10;
    $mul_rate['pp'] = 5;
    $mul_rate['v'] = 5;
    $mul_rate['y'] = 10;
    $mul_rate['IF'] = 300;
    $mul_rate['WS'] = 10;
    $mul_rate['ER'] = 10;
    $mul_rate['RO'] = 5;
    $mul_rate['WT'] = 10;
    $mul_rate['au'] = 1000;
    $mul_rate['ag'] = 15;
    $mul_rate['al'] = 5;
    $mul_rate['cu'] = 5;
    $mul_rate['pb'] = 5;
    $mul_rate['zn'] = 5;
    $mul_rate['ZW'] = 5000;
    $mul_rate['IH'] = 300;
    $mul_rate['IC'] = 200;
    $mul_rate['ni'] = 1;
    
    if(array_key_exists($symbol, $mul_rate)){
        return $mul_rate[$symbol];
    }
    return 1;
}

function get_contract_dbtable($contract)
{
    $symbol = preg_replace ('/(\d+)/i', '', $contract);  
    $contract_table["ru"] = "hq_shfe_k1";
    $contract_table["au"] = "hq_shfe_k1";
    $contract_table["rb"] = "hq_shfe_k1";
    $contract_table["ni"] = "hq_shfe_k1";
    $contract_table["ag"] = "hq_shfe_k1";
    $contract_table["al"] = "hq_shfe_k1";
    $contract_table["cu"] = "hq_shfe_k1";
    $contract_table["zn"] = "hq_shfe_k1";
    $contract_table["pb"] = "hq_shfe_k1";
    $contract_table["bu"] = "hq_shfe_k1";
    $contract_table["hc"] = "hq_shfe_k1";
    $contract_table["fu"] = "hq_shfe_k1";
    $contract_table["wr"] = "hq_shfe_k1";
    $contract_table["TA"] = "hq_czce_k1";
    $contract_table["FG"] = "hq_czce_k1";
    $contract_table["CF"] = "hq_czce_k1";
    $contract_table["SR"] = "hq_czce_k1";
    $contract_table["RM"] = "hq_czce_k1";
    $contract_table["MA"] = "hq_czce_k1";
    $contract_table["TC"] = "hq_czce_k1";
    $contract_table["OI"] = "hq_czce_k1";
    $contract_table["i"] = "hq_dce_k1";
    $contract_table["bb"] = "hq_dce_k1";
    $contract_table["c"] = "hq_dce_k1";
    $contract_table["fb"] = "hq_dce_k1";
    $contract_table["jd"] = "hq_dce_k1";
    $contract_table["l"] = "hq_dce_k1";
    $contract_table["pp"] = "hq_dce_k1";
    $contract_table["v"] = "hq_dce_k1";
    $contract_table["j"] = "hq_dce_k1";
    $contract_table["p"] = "hq_dce_k1";
    $contract_table["a"] = "hq_dce_k1";
    $contract_table["b"] = "hq_dce_k1";
    $contract_table["m"] = "hq_dce_k1";
    $contract_table["y"] = "hq_dce_k1";
    $contract_table["jm"] = "hq_dce_k1";
    $contract_table["IF"] = "hq_cffex_k1";
    $contract_table["IC"] = "hq_cffex_k1";
    $contract_table["IH"] = "hq_cffex_k1";
    $contract_table["TF"] = "hq_cffex_k1";
    $contract_table["T"] = "hq_cffex_k1";
    if(!array_key_exists( $symbol,$contract_table)) {
        return "";
    }
    return $contract_table[$symbol];
}
function get_inout_money($db, $account)
{
    if($db->connect()){
        $sql = sprintf("SELECT sum(money) as money FROM %s WHERE accountID='%s'", $GLOBALS['DB_TABLE_INOUT_MONEY'], $account);
        $recs = $db->executesql($sql);
        if($recs && count($recs) > 0 && $recs[0][0] > 0){
            return $recs[0][0];
        }
    }
    else{
        echo "cant connect db!";
    }
    
    return 5000000;
}

function get_account_base_money($db, $account)
{
    if($db->connect()){
        $sql = "SELECT base_money from fd_account WHERE account_symbol='".$account."'";
        $recs = $db->executesql($sql);
        if($recs && count($recs) > 0){
            return $recs[0][0];
        }
    }
    else{
        echo "cant connect db!";
    }
    
    return 5000000;
}

function get_trader_money($db, $account)
{
    if($db->connect()){
        $sql = "SELECT money FROM fd_report_trade_info WHERE name='".$account."'";
        $recs = $db->executesql($sql);
        if($recs && count($recs) > 0 ){
            return $recs[0][0];
        }
    }
    else{
        echo "cant connect db!";
    }
    
    return 0;   
}

function GetFundName($db, $fund_id)
{
    $sql = "SELECT name FROM fd_fund WHERE id=$fund_id";
    $recs = $db->executesql($sql);
    if ($recs && count($recs) > 0) {
        return $recs[0][0];
    }
    
    return "";
}

function GetAccountProfit($db, $id){
    $all_profit_single = array();
    $sql = "SELECT `time`,sum(profit) as profit FROM fd_report_profit WHERE accountID='$id' group by `time` order by `time`";
    $recs = $db->executesql($sql);
    if($recs && count($recs) > 0){
        foreach ($recs as $rec) {
            $all_profit_single[$rec[0]] = $rec[1];
        }
    }
    return $all_profit_single;
}

?>