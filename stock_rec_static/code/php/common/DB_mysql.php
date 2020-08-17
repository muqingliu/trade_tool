<?php
class Database{
    private $host;
    private $port;
    private $username;
    private $password;
    private $dbname;
                                       
    public function __construct($Re_Host,$Re_Port,$Re_Username,$Re_Password,$Re_Dbname){
            $this->host=$Re_Host;
            $this->port=$Re_Port;
            $this->username=$Re_Username;
            $this->password=$Re_Password;
            $this->dbname=$Re_Dbname;
    }
    
    public function __destruct(){
            $this->host=null;
            $this->port=null;
            $this->username=null;
            $this->password=null;
            $this->dbname=null;
            $this->connect=null;
            @mysql_close();
    }                
    
    function version() {
            if(empty($this->version)) {
                    $this->version = mysql_get_server_info($this->connect);
            }
            return $this->version;
    }

    public function connect(){
		$host = $this->host;
		if($this->port) $host = $this->host.":".$this->port; 
        $this->connect = @mysql_connect($host,$this->username,$this->password);
        if ($this->connect != null){
            
            if($this->version() > '4.1') {
                                $bidcmscharset ="utf8";
                                $bidcmsdbcharset = "utf8";	
				$dbcharset = $bidcmsdbcharset;
				$dbcharset = !$dbcharset && in_array(strtolower($bidcmscharset), array('utf-8', 'big5', 'utf8','gbk')) ? str_replace('-', '', $bidcmscharset) : $dbcharset;
				$serverset = $dbcharset ? 'character_set_connection='.$dbcharset.', character_set_results='.$dbcharset.', character_set_client='.$dbcharset : '';
				$serverset .= $this->version() > '5.0.1' ? ((empty($serverset) ? '' : ',').'sql_mode=\'\'') : '';
				$serverset && mysql_query("SET $serverset", $this->connect);
			}
            return $this->connect;
        }
        else{
			echo mysql_error(). " host:" . $host ."<br>"; 
            return false;
        }
    }
    
    private function selectdb(){
        if ($this->connect()!=false){
            return (@mysql_select_db($this->dbname));
        }
        else{
            return false;
        }                
    }
    
    public function getEffectRows(){  
        $num = mysql_affected_rows();  
        return $num;
    }
    
    public function executesql($sql){
        if ( !isset($sql) || empty($sql) || !$this->selectdb()){
            return false;
        }

        $result = null;
        $result = @mysql_query($sql);

        if ($result === true){
            return true;
        }            
        else if ($result === false || !isset($result)){
            // SQL 错误或无效
            return false;
        }
        else{
            $return_result = array();
            $count = mysql_num_rows($result);
            if ($count > 0){
                $i = 0;
                while($rec = @mysql_fetch_array($result)){
                   $return_result[$i++]= $rec;
                }                        
            }
            return $return_result;
        }
    } 
    
    public function makeSelectSql($table, $param, $cond){
        $sql = 'select ';
        if (!is_array($param) && strstr($param, "*") != null) {
            $sql = $sql."* from ".$table;
        }
        else {
            foreach ($param as $key) {
                if($sql != 'select '){
                    $sql .= ',';
                }
                
                $sql .= "{$key}";
            }
            $sql .= " from ".$table;
        }
        
        if ($cond) {
            $sql .= " where {$cond}";
        }
        
        return $sql;
    }

    public function makeUpdateSql($table, $param, $cond){
        $sql = 'update `'. $table. '` set ';
        foreach($param as $key=>$val){
            
            if($sql != 'update `'. $table. '` set '){
                
                $sql .= ',';
            }

            $sql .= "`{$key}`='{$val}'";
        }
        if($cond){
            $sql .= " where {$cond}";
        }
        return $sql;
    }

    public function makeInsertSql($table, $param){
        $sql = 'insert into `'. $table. '` (';
        $keys = array_keys($param);
        $sql .= '`'. implode('`,`', $keys). '`) values (';
        $sql .= '\''. implode('\',\'', $param). '\')';
        return $sql;
    }

    public function makeDeleteSql($table, $cond){
        $sql = 'delete from `'.$table.'`';
        
        if($cond){
            $sql .= " where {$cond}";
        }
        return $sql;
    }

    public function makeReplaceSql($table, $param){
        $sql = 'replace into `'. $table. '` (';
        $keys = array_keys($param);
        $sql .= '`'. implode('`,`', $keys). '`) values (';
        $sql .= '\''. implode('\',\'', $param). '\')';
        return $sql;
    }
}
?>
