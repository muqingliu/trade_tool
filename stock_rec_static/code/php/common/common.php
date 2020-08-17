<?php

require_once "connInfo.php";
require_once "DB_mysql.php";
require_once "DB_sqlite.php";

// date_default_timezone_set("Asia/Shanghai");

// $companyName = "微创科技量化投资";

class databaseInfo {
    public $ip;
    public $account;
    public $password;
    public $dbname;      
    public $port;
    public function __construct($a, $p, $ip, $dbname, $port)
    {
        $this->account = $a;                    
        $this->password= $p;
        $this->ip=$ip;
        $this->dbname = $dbname;        
        $this->port =$port;
    }        
}

function write_log($fileName, $content){
    if(!is_readable("log")){
        mkdir('log');
    }

    $logFileName = "log/".$fileName."-".date("Y-m-d").".log";     
    $james=fopen($logFileName,"a+");
    fwrite($james,date("Y-m-d H:i:s")."\t".$content."\r\n"); 
    fclose($james);
}

function CreateDatabase()
{
    if ($GLOBALS['sql_mode'] == 0) {
        $server = new databaseInfo($GLOBALS['DB_USER'], $GLOBALS['DB_PWD'], $GLOBALS['DB_HOST'], $GLOBALS['DB_DATABASE'], $GLOBALS['DB_PORT']);
        $db = new Database($server->ip, $server->port, $server->account, $server->password, $server->dbname);
        if ($db->connect()){
            return $db;
        }
    }
    else {
        $db = new sqlite($GLOBALS['DB_PATH']);
        if($db){
            return $db;
        }       
    }

    echo "cant connect db database!";
    return null;
}

function CreateDatabaseData()
{
    if ($GLOBALS['sql_mode'] == 0) {
        $server = new databaseInfo($GLOBALS['DB_USER'], $GLOBALS['DB_PWD'], $GLOBALS['DB_HOST'], $GLOBALS['DB_DATABASE_STOCK_DATA'], $GLOBALS['DB_PORT']);
        $db = new Database($server->ip, $server->port, $server->account, $server->password, $server->dbname);
        if ($db->connect()){
            return $db;
        }
    }
    else {
        $db = new sqlite($GLOBALS['DB_PATH_STOCK_DATA']);
        if($db){
            return $db;
        }
    }

    echo "cant connect db database!";
    return null;
}

function CreateDatabaseEx($user, $pwd, $host, $database, $port)
{
    $server = new databaseInfo($user, $pwd, $host, $database, $port);
    $db = new Database($server->ip, $server->port, $server->account, $server->password, $server->dbname);
    if ($db->connect()){
        return $db;
    }
    echo "cant connect db $database!";
    return null;
}


function get_next_day($date, $add_days = 1){
    $date = intval($date);
    $y = $date / 10000;
    $m = $date / 100 % 100;
    $d = $date  % 100;
    return date("Ymd", mktime(0,0,0,$m, $d + $add_days, $y));
}

function diff_days($date_first, $date_second)
{
    $days = round((strtotime($date_second) - strtotime($date_first)) / 3600 / 24);
    return $days;
}

function httpPost($url, $parms){
    if (($ch = curl_init($url)) == false) {
        throw new Exception(sprintf("curl_init error for url %s.",$url));
    }

    curl_setopt($ch, CURLOPT_POST, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_HEADER ,0);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT,600);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);

    if(is_array($parms)){
        curl_setopt($ch, CURLOPT_POSTFIELDS, $parms);
        curl_setopt($ch, CURLOPT_HTTPHEADER,array('Content-Type: multipart/form-data;')); 
    }

    $postResult = @curl_exec($ch);
    $http_code = curl_getinfo($ch,CURLINFO_HTTP_CODE);
    if ($postResult===false || $http_code != 200 || curl_errno($ch)) {
        $error= curl_error($ch);
        curl_close($ch);
        throw new Exception("HTTP POST FAILED:$error");        
    }else{
        $postResult=str_replace("\xEF\xBB\xBF", '', $postResult);
        switch(curl_getinfo($ch,CURLINFO_CONTENT_TYPE)){
            case 'application/json':
                $postResult=json_decode($postResult);
                break;
        }

        curl_close($ch);
        return $postResult;
    }
}
?>