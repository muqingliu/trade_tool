<?php
require_once "common.php";
require_once "common_trade.php";

define('DIR_BUY',  0);
define('DIR_SELL', 1);
define('TYPE_OPEN', 0);
define('TYPE_CLOSE', 1);

class CPosition{
    public function __construct($contract, $datetime, $dir, $number, $price){
        $this->contract = $contract;
        $this->datetime = $datetime;
        $this->dir = $dir;
        $this->number = $number;
        $this->price = $price;
        $this->day_counter = 0;
    }
}

class CPositionsManager{
    public function __construct($errmsg_immediate = false, $merge = false, $houseware = ""){
        $this->contracts = array();
        $this->total_profit  = array();
        $this->total_diviend = array(); // 分红
        $this->total_tax = array(); // 所得税
        $this->total_commission = array();
        $this->securities = array();
        $this->margin_pos = array();
        $this->err_msg = array();
        $this->errmsg_immediate = $errmsg_immediate;
        $this->merge = $merge;
        $this->houseware = $houseware;
    }

    public function open($datetime, $contract, $dir, $number, $price, $commission){
        $number = abs($number);
        if (0 == $number || $price <= 0) {
            return;
        }
        
        if(!array_key_exists($contract, $this->contracts)){
            $this->contracts[$contract] = array();
            $this->contracts[$contract][DIR_BUY] = array();
            $this->contracts[$contract][DIR_SELL] = array();
        }

        if($this->merge){
            if(count($this->contracts[$contract][$dir]) == 0){ 
                $this->contracts[$contract][$dir][] = new CPosition($contract, $datetime, $dir, $number, ($price * $number + $commission) / $number);
            }
            else{
                $total_number = $this->contracts[$contract][$dir][0]->number + $number;
                $total_price = $this->contracts[$contract][$dir][0]->number * $this->contracts[$contract][$dir][0]->price + $number * $price + $commission;
                $this->contracts[$contract][$dir][0]->number = $total_number;
                $this->contracts[$contract][$dir][0]->price = $total_price / $total_number;
            }
        }
        else{
            $this->contracts[$contract][$dir][] = new CPosition($contract, $datetime, $dir, $number, $price);
        }

        if(!array_key_exists($contract, $this->total_profit)){
            $this->total_profit[$contract] = 0;
            $this->total_commission[$contract] = $commission;
        }
        else{
            $this->total_commission[$contract] += $commission;
        }	    
    }

    public function close($datetime, $contract, $dir, $number, $price, $commission, $today, &$log){
        $number = abs($number);
        if (0 == $number || $price <= 0) {
            return;
        }
        
        if(!array_key_exists($contract, $this->contracts)){
            $err = sprintf('sell error, not match contract[%s] date[%s] dir[%s] number[%s] price[%.2f]<br>' ,$contract, $datetime, $dir, $number, $price);
            $this->err_msg[] = $err;
            if($this->errmsg_immediate){
                write_log("pos_error", "文件[".$this->houseware."] ".$err);
                $log["pos"][] = "文件[".$this->houseware."] ".$err;
            }
            return;
        }

        $total_sell = $number;
        $total_profit = 0;
        $positions = &$this->contracts[$contract][1-$dir];
        $index = 0;
        while(true){
            if(count($positions) == 0) break;
            $pos = &$positions[$index];

            $remove_number = 0;
            if (!$this->merge) {
                if($today && floor($pos->datetime/1000000) != floor($datetime/1000000)){ # 如果是平今，但是该仓非今仓          
                    $loop_count = 0;
                    while(true){
                        $index += 1;
                        $loop_count +=1;
                        $pos = &$positions[$index];
                        if(floor($pos->datetime/1000000) == floor($datetime/1000000)) break;
                        if($loop_count > 50){
                            $err = sprintf('sell error, cant find close today position [%s] date[%s] dir[%d] number[%s] price[%.2f]<br>', $contract, $datetime, $dir, $number, $price);
                            $this->err_msg[] = $err;
                            if($this->errmsg_immediate){
                                // echo $err;
                                write_log("pos_error", "文件[".$this->houseware."] ".$err);
                                $log["pos"][] = "文件[".$this->houseware."] ".$err;
                            }
                            return -1;
                        }
                    }
                }
                
                $remove_number = min($pos->number, $total_sell);

                if($dir == DIR_SELL){
                    $total_profit += $remove_number * ($price - $pos->price) * get_contract_mutil($contract);
                }
                else{
                    $total_profit += $remove_number * ($pos->price - $price) * get_contract_mutil($contract);
                }
                
                $total_sell -= $remove_number;
                $pos->number -= $remove_number;
            }
            else {
                $remove_number = min($pos->number, $total_sell);
                
                $total_pos_price = $pos->price * $pos->number + $commission;
                $total_price = $price * $remove_number;
                
                $total_sell -= $remove_number;
                $pos->number -= $remove_number;
                if ($pos->number > 0) {
                    $pos->price = ($total_pos_price - $total_price) / $pos->number;
                }
                else {
                    $total_profit = $total_price - $total_pos_price;
                }
            }
            
            if($pos->number == 0){array_splice($positions, $index, 1);}
            if($total_sell == 0){ break;}
        }

        $this->total_profit[$contract] += $total_profit;
        $this->total_commission[$contract] += $commission;            

        if($total_sell > 0){ 
            $err = sprintf('sell error, not match contract[%s] date[%s] dir[%s] number[%s] price[%.2f]<br>', $contract, $datetime, $dir, $number, $price);
            $this->err_msg[] = $err;
            if($this->errmsg_immediate){
                // echo $err;
                write_log("pos_error", "文件[".$this->houseware."] ".$err);
                $log["pos"][] = "文件[".$this->houseware."] ".$err;
            }
            return;
        }
        # 手续费累加;
        return $total_profit;
    }
    
    // 利息归本
    public function Interest($Interest){
        if(!array_key_exists("lx", $this->total_profit)) {
            $this->total_profit["lx"] = 0;
        }
        $this->total_profit["lx"] += $Interest;
    }
    
    // 融券
    public function SecuritiesLending($contract, $Securities, $commission){    
        if(!array_key_exists($contract, $this->securities)) {
            $this->securities[$contract] = $Securities;
        }
        else {
            $this->securities[$contract] += $Securities;
        }
        
        if(!array_key_exists($contract, $this->total_profit)){
            $this->total_profit[$contract] = 0;
            $this->total_commission[$contract] = $commission;
        }
        else{
            $this->total_commission[$contract] += $commission;
        }
    }
    
    // 融券购回
    public function SecuritiesRepurchase($contract, $Securities, $commission){
        if(!array_key_exists($contract, $this->securities)) {
            return;
        }
        $profit = $Securities - $this->securities[$contract];
        $this->securities[$contract] = 0;
        
        $this->total_profit[$contract] += $profit;
        $this->total_commission[$contract] += $commission;
    }
    
    // 保证金产品申购
    public function margin_buy($contract, $num, $commission){
        if(!array_key_exists($contract, $this->margin_pos)) {
            $this->margin_pos[$contract] = $num;
        }
        else {
            $this->margin_pos[$contract] += $num;
        }
        
        if(!array_key_exists($contract, $this->total_profit)){
            $this->total_profit[$contract] = 0;
            $this->total_commission[$contract] = $commission;
        }
        else{
            $this->total_commission[$contract] += $commission;
        }
    }
    
    // 保证金产品赎回
    public function margin_redeem($contract, $num, $commission){
        if(!array_key_exists($contract, $this->margin_pos)) {
            return;
        }
        $this->margin_pos[$contract] = max($this->margin_pos[$contract] - $num, 0);
        
        $this->total_commission[$contract] += $commission;
    }

    // 分红所得税
    public function pay_tax($contract, $tax){
        if(!array_key_exists($contract, $this->total_tax)) {
            $this->total_tax[$contract] = 0;
        }
        $this->total_tax[$contract] += $tax;
    }

    // 分红
    public function diviend($contract, $date, $diviend){
        if(!array_key_exists($contract, $this->total_diviend)) {
            $this->total_diviend[$contract] = 0;
        }
        $this->total_diviend[$contract] += $diviend;
        
        if(array_key_exists($contract, $this->contracts) && count($this->contracts[$contract][DIR_BUY]) > 0){
            $pos = &$this->contracts[$contract][DIR_BUY][0];
            if ($pos->number > 0) {
                $pos->price -= $diviend / $pos->number;
            }
        }
        else if (array_key_exists($contract, $this->margin_pos)) {
            $this->total_profit[$contract] += $diviend;
        }
    }
    
    public function allotment($contract, $date, $diviend_qty){
        if(array_key_exists($contract, $this->contracts) && count($this->contracts[$contract][DIR_BUY]) > 0){
            $pos = &$this->contracts[$contract][DIR_BUY][0];
            $total_price = $pos->price * $pos->number;
            $pos->number = $pos->number + $diviend_qty;
            $pos->price = $total_price / $pos->number;
        }
    }

    public function get_contracts(){
//        $contracts = array();
//        foreach ($this->contracts as $contract => $positions) {
//            $volume = 0;
//            for($i =0; $i<2; $i++){
//                foreach($positions[$i] as $pos){
//                    $volume += $pos->number;
//                }
//            }
//            
//            if ($volume > 0) {
//                $contracts[] = $contract;
//            }
//        }
//        return $contracts;
        
        $pos_array = array_keys($this->contracts);
        $margin_pos_array = array_keys($this->margin_pos);
        $securities_array = array_keys($this->securities);
        $merge_array = array_merge($pos_array, $margin_pos_array);
        $merge_array = array_merge($merge_array, $securities_array);
        return $merge_array;
    }
    
    public function get_pos_contracts(){
        $contracts = array();
        foreach ($this->contracts as $contract => $positions) {
            $volume = 0;
            for($i =0; $i<2; $i++){
                foreach($positions[$i] as $pos){
                    $volume += $pos->number;
                }
            }
            
            if ($volume > 0) {
                $contracts[] = $contract;
            }
        }
        
        foreach ($this->margin_pos as $contract => $num) {
            if ($num > 0) {
                $contracts[] = $contract;
            }
        }

        foreach ($this->securities as $contract => $num) {
            if ($num > 0) {
                $contracts[] = $contract;
            }
        }
        
        return $contracts;
    }
    
    public function get_contract_ave_price($dir)
    {
        $contract_ave_price = array();
        foreach ($this->contracts as $contract => $positions) {
            $total_price = 0;
            $total_number = 0;
            foreach ($positions[$dir] as $pos) {
                $total_price = $total_price + $pos->number * $pos->price;
                $total_number = $total_number + $pos->number;
            }
            
            if ($total_number > 0) {
                $contract_ave_price[$contract] = $total_price / $total_number;
            }
        }
        
        foreach ($this->margin_pos as $contract => $num) {
            $contract_ave_price[$contract] = 1;
        }
        
        return $contract_ave_price;
    }

    public function get_position_profit($contrace_price, $date){
        $total_profit = 0;
        foreach($this->contracts as $positions){
            foreach($positions[DIR_BUY] as $pos){
                if(array_key_exists($pos->contract, $contrace_price)) {
                    $total_profit += $pos->number * ($contrace_price[$pos->contract] - $pos->price) * get_contract_mutil($pos->contract);
                }
                else{
                    write_log("miss price", "文件[".$this->houseware."] date:".$date." contract:".$pos->contract);
                }
            }

            foreach($positions[DIR_SELL] as $pos){
                if(array_key_exists($pos->contract, $contrace_price)) {
                    $total_profit += $pos->number * ($pos->price - $contrace_price[$pos->contract]) * get_contract_mutil($pos->contract);
                }
                else{
                    write_log("miss price", "文件[".$this->houseware."] date:".$date." contract:".$pos->contract);
                }
            }
        }
        return $total_profit;
    }

    public function get_contract_position_profit($contract, $price, $dir = null){
        $total_profit = 0;
        foreach($this->contracts as $positions){
            if ($dir == null) {
                foreach($positions[DIR_BUY] as $pos){
                    if($pos->contract == $contract){
                        $total_profit += $pos->number * ($price - $pos->price) * get_contract_mutil($pos->contract);
                    }
                }

            foreach($positions[DIR_SELL] as $pos){
                if($pos->contract == $contract) {
                        $total_profit += $pos->number * ($pos->price - $price) * get_contract_mutil($pos->contract);
                    }
                }
            }
            else {
                foreach ($positions[$dir] as $pos) {
                    if($pos->contract == $contract){
                        if($dir == DIR_BUY) {
                            $total_profit += $pos->number * ($price - $pos->price) * get_contract_mutil($pos->contract);
                        }
                        else if($dir == DIR_SELL) {
                            $total_profit += $pos->number * ($pos->price - $price) * get_contract_mutil($pos->contract);
                        }
                    }                   
                }
            }
        }
        return $total_profit;
    }
    
    public function get_diviend($contract){
        if (array_key_exists($contract, $this->total_diviend)) {
            return $this->total_diviend[$contract];
        }
        
        return 0;
    }

    public function get_volume($contract_symbol){          
        $volume = array(0,0);
        foreach($this->contracts as $contract => $positions){
            if(strcmp($contract,$contract_symbol) == 0){
                for($i =0; $i<2; $i++){
                    foreach($positions[$i] as $pos){
                        $volume[$i] += $pos->number;
                    }
                }
            }
        }
        foreach($this->margin_pos as $contract => $num){
            if(strstr($contract,$contract_symbol)){
                $volume[0] += $num;
            }            
        }
        return $volume;
    }

    public function get_profit($contract=null){
        if($contract){
            if(array_key_exists($contract, $this->total_profit)){
                $total_profit = $this->total_profit[$contract];
                if(array_key_exists($contract, $this->total_tax)) {
                    $total_profit += $this->total_tax[$contract];
                }
                return $total_profit;
            }
            return 0;
        }
        else{
            $total_profit = 0;
            foreach($this->total_profit as $c=>$v){
                $total_profit += $v;
                if(array_key_exists($c, $this->total_tax)) {
                    $total_profit += $this->total_tax[$c];
                }
            }
            return $total_profit;
        }
    }

    public function get_commission($contract=null){
        if($contract){
            if(array_key_exists($contract, $this->total_commission)) {
                return $this->total_commission[$contract];
            }
            return 0;
        }
        else{
            $total = 0;
            foreach($this->total_commission as $c=>$v){
                $total += $v;
            }
            return $total;
        }
    }

    public function ex_right_price($db, $date){
        if (!$this->merge) {
            return;
        }

        $contracts = array_keys($this->contracts);
        $sql = sprintf("SELECT * FROM %s WHERE id in (%s) and date=%u", $GLOBALS['DB_TABLE_DIVIDEND_ALLOTMENT'], 
            "'".str_replace(",","','",join(",",$contracts))."'", $date);
        $recs = $db->executesql($sql);
        foreach ($recs as $rec) {
            $contract = $rec['id'];
            $transfer = $rec['transfer'];
            $qty = $rec['qty'];
            $dividend_price = $rec['price'];
            $dividend = $rec['dividend'];

            if (array_key_exists($contract, $this->contracts) && count($this->contracts[$contract][DIR_BUY]) > 0) {
                $positions = &$this->contracts[$contract];
                $pos = &$positions[DIR_BUY][0];

                $dividend_money = floor($pos->number/10) * $dividend * 0.9;
                if(!array_key_exists($contract, $this->total_diviend)) {
                    $this->total_diviend[$contract] = 0;
                }
                $this->total_diviend[$contract] += $dividend_money;

                $dividend_qty = floor($pos->number/10) * $qty;
                if ($dividend_qty > 0) {
                    $pos->number = $pos->number + $dividend_qty;
                }

                $dividend_transfer = floor($pos->number/10) * $transfer;
                if ($dividend_transfer > 0) {
                    $pos->number = $pos->number + $dividend_transfer;
                }

                $pos->price = ($pos->price + $qty/10*$dividend_price - $dividend*0.9/10) / (1+$transfer/10 + $qty/10);
            }
        }
    }

    public function show_error(){
        foreach($this->error_msg as $msg){
            echo $msg."<br>";
        }
    }
    
    public function increase_day_counter($dir=0)
    {
//   print_r("<br>");
        foreach($this->contracts as $positions) {
            foreach ($positions[$dir] as $pos) {
                $pos->day_counter+=1;
            }
//            print_r($positions);
        }

    }

    public function get_stock_day_counter($contract=null,$dir=0)
    {
        $day_counter=-1;
        if(array_key_exists($contract, $this->contracts) && count($this->contracts[$contract][DIR_BUY]) > 0)
        {
            $day_counter =$this->contracts[$contract][$dir][0]->day_counter;
        }
        return $day_counter;

    }
}

