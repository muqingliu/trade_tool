<?php
require_once "Common.php";
require_once "DB.php";

$db_path = "res/db/stock_static.db";
$db = new sqlite($db_path);
if(!$db){
    return;
}

function clear_db($db){
	$sql = sprintf("DELETE FROM ss_k_data");
	$db->executesql($sql);
}

clear_db($db);

?>