<?php

if (file_exists("system.ini")) {
    $sys_ini_array = parse_ini_file("system.ini", true);
    if (null == $sys_ini_array) {
        write_log("error", "配置文件[system.ini]解析失败");
        return;
    }
    $GLOBALS['sql_mode'] = $sys_ini_array["main"]["sql_mode"];
}

if ($GLOBALS['sql_mode'] == 0) {
	require_once "DB_mysql.php";
}
else {
	require_once "DB_sqlite.php";
}

?>