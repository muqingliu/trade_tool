<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>5656K 股票分析网</title><meta name="keywords" content="" />

    <script type="text/javascript" src="res/js/jquery-1.7.2.min.js"></script>
    <script src="res/js/common.js" language="javascript" type="text/javascript"></script>
</head>
<?php

function get_extension($file){
    $info = pathinfo($file);
    return $info['extension'];
}

if(array_key_exists( 'file',$_FILES)) {
    //$filename = $_FILES["file"]["tmp_name"];
    $info = pathinfo($_FILES['file']['name']);
    $file_new =$info["filename"]."_".date("Ymdhis").".".$info["extension"];
    if(!move_uploaded_file($_FILES['file']['tmp_name'],"res/db/".$file_new)){
        echo "上传错误";
        return;
    }
}

?>


<body STYLE='OVERFLOW:SCROLL;OVERFLOW-X:HIDDEN'>
<form action="stock_static.php?upload=ok" method="post"
      enctype="multipart/form-data">
<!--     <label for="file">上传交易记录:</label>
    <input type="file" name="file" id="file" />
    <br />
    <input type="submit" name="submit" value="提交" /> -->
</form>

<?php
if(array_key_exists( 'file',$_FILES)){
?>
<div id="container">
    <!-- START PAGE -->

    <div id="img_container"><div style="padding-top:20px;font-size:14px;"><img src='images/load.gif' width='20' height='20' style='vertical-align:middle;' /> 数据读取中,请稍候...</div></div>
    <div id="test" align='left'></div>
    <div class="panel datagrid">
        <div class="datagrid-wrap panel-body panel-body-noheader">
            <b><div id='user_id'></div></b><a id='log_link' href="javascript:void(0);" onclick="ShowLogWin()" style="color:red;display:none">查看错误日志</a>
            <div id='money'></div>
            <div id='grid_contract'></div>  
        </div>
    </div>
    <div id="window_log">
        <div id="log_datagrid">
        
        </div>
    </div>
    <link rel="stylesheet" type="text/css" href="res/css/easyui.css">
    <script type="text/javascript" src="res/js/jquery-1.7.2.min.js"></script>
    <script type="text/javascript" src="res/js/jquery.easyui.min.js"></script>
    <script type="text/javascript" src="res/js/highcharts.js"></script>
    <script type="text/javascript">
        <!--
        function imt(d){
            return Date.UTC(parseInt(d/10000), parseInt(d/100%100)-1, parseInt(d%100));
        }
        //-->
    </script>
    <script type="text/javascript">
        function default_tooltip_fun(chart)
        {
            return '<b>'+ chart.series.name +'</b><br/>' + Highcharts.dateFormat('%Y-%m-%d', chart.x) + ': '+ chart.y +'';
        }

        function numberSort(a,b){  
            var number1 = parseFloat(a);  
            var number2 = parseFloat(b);  

            return (number1 > number2 ? 1 : -1); 
        }
        
        function queryAccountInfo(account_info){
            $("#user_id").html(account_info.user_id);
            $("#money").html(account_info.money);
        }
        
        function SetGrid(gridName, datas){
            var column_info = [[
                { field: 'contract', title: 'ID', width: 60, align: 'left', sortable: true },
                { field: 'name', title: '合约', width: 70, align: 'left' },
                { field: 'volume', title: '持仓数量', width: 60, align: 'right' },
                { field: 'ave_price', title: '成本', width: 55, align: 'right' },
                { field: 'open_price', title: '开盘价', width: 55, hidden: true },
                { field: 'now_price', title: '现价', width: 55, align: 'right' }, 
                { field: 'floatProfit', title: '盈亏金额', width: 90, align: 'right', sortable: true, sorter: numberSort },
                { field: 'ratio', title: '比例', width: 70, align: 'right', sortable: true, sorter: numberSort },
                { field: 'marketValue', title: '市值', width: 90, align: 'right', sortable: true, sorter: numberSort }
            ]];

            $('#'+gridName).datagrid({
                idField: '合约',
                remoteSort: false,
                rownumbers: true,
                fitColumns: true,
                showFooter: true,
                striped: true,
                singleSelect: true,
                pagination: false,
                nowrap: false,
                toolbar: '#title_' + gridName,
                columns: column_info,
                data: datas,
                rowStyler:function(index,row){
                    if (row.open_price == 0){
			return 'color:#008000';
                    }
                    else {
                        if (parseFloat(row.floatProfit) > 0){
                            return 'color:#FF0000;';
                        }
                        else if (parseFloat(row.floatProfit) < 0) {
                            return 'color:#0000FF';
                        }                        
                    }
		},
                onBeforeLoad: function (param) {
                },
                onLoadSuccess: function (data) {
                },
                onLoadError: function () {
                },
                onClickCell: function (rowIndex, field, value) {
                }
            });
        }
        
        function show_chart(title, account_info, intv, min_value, categories, series, contract_table_res, mark_enable, tooltip_fun){
            var chart;
            $(document).ready(function() {
                chart = new Highcharts.Chart({
                    chart: {
                        renderTo: 'img_container',
                        zoomType: 'x',
                        defaultSeriesType: 'spline',
                        height:800
                    },
                    title: {
                        text: title,
                        x: -20 //center
                    },
                    subtitle: {
                        text: 'Source: 5656K',
                        x: -20
                    },
                    xAxis: {
                        type: 'datetime',
                        labels: {
                             step: 3,
                            formatter: function () {
                                return Highcharts.dateFormat('%Y-%m-%d', this.value);
                            }
                        },
                        //categories: categories,
                    },
                    yAxis: {
                        min:min_value,
                        /*max:12,*/
                        tickInterval:intv,
                        labels: {
                            formatter: function() {
                                return this.value.toFixed(6);//这里是两位小数，你要几位小数就改成几
                            },
                            style: {
                                color: 'black'
                            }
                        },
                        title: {
                            text: null
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    tooltip: {
                        shared: true, 
                        useHTML:true,
                        crosshairs:[
                            {   enabled:true,
                                width:1,//标线宽度
                                color:'red' //标线颜色值
                            }
                        ],
                        //xDateFormat: '%Y-%m-%d',//鼠标移动到趋势线上时显示的日期格式
                        formatter: function() {
                            if(tooltip_fun) return tooltip_fun(this);
                            return default_tooltip_fun(this);
                        }
                    },
                    plotOptions: {
                        spline: {
                            lineWidth: 2,
                            states: {
                                hover: {
                                    lineWidth: 3
                                }
                            }
                        }
                    },
                    series: series
                });
                
                queryAccountInfo(account_info);
                SetGrid("grid_contract", contract_table_res);
            });
        }
        
        function CreateLogWin(log_list, count){
            var winName = "window_log";
            $('#' + winName).window({
                width:580,
                height:400,
                title:"日志",
                iconCls:'icon-save',
                closed:true,
            });

            var gridName = "log_datagrid";
            SetLogGrid(gridName, log_list, count);
            
            var log_link =document.getElementById("log_link");
            log_link.style.display="block";
        }
        
        function ShowLogWin()
        {
            var winName = "window_log";
            $('#' + winName).window('open');
        }
        
        function SetLogGrid(gridName, log_list, count)
        {
            var columes = [
                { field: 'log', title: '日志', width: 564, align: 'left' },
            ];

           $('#' + gridName).datagrid({
            fit: true,
            striped: true,
            singleSelect: true,
            rownumbers: false,
            pagination: false,
            nowrap: false,
            toolbar:'#title_' + gridName,
            columns: [columes],
           });
           $('#' + gridName).datagrid("loadData",{"total":count,"rows":log_list});  
        }

//        $.ajax({
//            type: "post",
//            url: "service_stock_static.php?f=<?php #echo $file_new;?>",
//            success: function (relt) {
        var obj = eval('('+result+')');
        eval(obj.script);
        show_chart("资金曲线", obj.account_info, obj.interval, obj.min_value, eval(obj.categories), eval(obj.series), obj.contract_table_res, false, tooltip_fun);
        if (obj.log_count > 0) {
            CreateLogWin(obj.log_rows, obj.log_count);
        }
//        })

    </script>
</div>
<?php }?>

</body>
