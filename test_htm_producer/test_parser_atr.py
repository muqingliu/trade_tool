template ="""
<!DOCTYPE html>
<head>
    <meta charset="utf-8">
    <title><<!!contract>></title>
</head>
<h2><<!!contract>></h2>
<body>
    <<!!linkbutton>>
    <!-- 为ECharts准备一个具备大小（宽高）的Dom -->
    <div id="main1" style="width:1620px; height:400px"></div>
    <div id="main2" style="width:1620px; height:400px"></div>
    <div id="main3" style="width:1620px; height:400px"></div>
    <div id="main4" style="width:1620px; height:400px"></div>
    <div id="main5" style="width:1620px; height:400px"></div>
    <div id="main6" style="width:1620px; height:400px"></div>
    <div id="main7" style="width:1620px; height:400px"></div>
    <div id="main8" style="width:1620px; height:400px"></div>
    <!-- ECharts单文件引入 -->
    <script src="../../js/echarts.js"></script>
    <script src="../../js/common_echart.js"></script>
    <link rel="stylesheet" type="text/css" href="../../css/default.css">
    <link rel="stylesheet" type="text/css" href="../../css/easyui.css">
    <script type="text/javascript" src="../../js/jquery.min.js"></script>
    <script type="text/javascript" src="../../js/jquery.easyui.min.js"></script>
    <script type="text/javascript">
        // 使用
        chart_draw_line_bar(echarts, "main1", "利润保证金图", "利润", "保证金率", [<<!!xAxis>>], <<!!series1>>);
        chart_draw_line_bar(echarts, "main2", "利润回撤图", "利润", "回撤", [<<!!xAxis>>], <<!!series2>>);
        chart_draw_line_bar_color(echarts, "main3", "平仓保证金率图", "平仓利润", "保证金率", [<<!!xAxis>>], <<!!pieces>>, <<!!series3>>);
        chart_draw_line_bar_color(echarts, "main4", "平仓回撤图", "平仓利润", "平仓回撤", [<<!!xAxis>>], <<!!pieces>>, <<!!series4>>);
        chart_draw_double_bar(echarts, "main5", "盈利周期图", ["回调天数","回补天数"], "天数", [<<!!xAxis1>>], <<!!series5>>);
        chart_draw_double_bar(echarts, "main6", "顺序回撤图", ["回撤","当前回撤"], "百分比", [<<!!xAxis2>>], <<!!series6>>);
        chart_draw_bar(echarts, "main7", "月度收益图", "单月收益", [<<!!xAxis3>>], <<!!series7>>);
        chart_draw_line(echarts, "main8", "历史atr图", ["atr"], "atr", [<<!!xAxis4>>], <<!!series8>>);
    </script>
</body>
"""


import test_parser_base
import pyetc
import os
import json


class TestParserAtr(test_parser_base.TestParserBase):
    """docstring for TestParserAtr"""
    def __init__(self):
        super(TestParserAtr, self).__init__()

        
    def judge_test_file(self, contract, parent, filename, map_test_file):
        super(TestParserAtr, self).judge_test_file(contract, parent, filename, map_test_file)

        if filename.find("_atr.log") >= 0:
            full_file_path = os.path.join(parent,filename)
            map_test_file[contract]["atr"] = full_file_path


    def read_atr(self, filename):
        datas = [[],[]]
        with open(filename, 'rb') as f:
            line = f.readline()
            while line:
                eles = line.split('\t')
                time = test_parser_base.parse_date(eles[0])
                atr = float(eles[1])

                datas[0].append(eles[0])
                datas[1].append(atr)
                line = f.readline()

        return datas


    def create_result_web(self, template, contract, map_test_file):
        content = super(TestParserAtr, self).create_result_web(template, contract, map_test_file)

        datas_atr = self.read_atr(map_test_file["atr"])

        dates_atr = ["'" + e + "'" for e in datas_atr[0]]
        dates_atr_str = (',').join(dates_atr)
        content = content.replace('<<!!xAxis4>>', dates_atr_str)

        series_atr = {'name':'atr',
            'type':'line',
            'symbolSize' : '0',
            'data':datas_atr[1],
            }

        series8 = [series_atr]
        content = content.replace('<<!!series8>>', json.dumps(series8))

        return content


def main():
    config = pyetc.load(r'system.ini')

    test_parser_model = TestParserAtr()
    map_test_file = test_parser_model.find_test_file(config.test_result_path)
    for contract in map_test_file:
        test_result_files = map_test_file[contract]
        if len(test_result_files) == 0:
            continue

        print contract
        content = test_parser_model.create_result_web(template, contract, test_result_files)

        full_result_path = test_parser_model.get_web_path(config.web_path, config.policy, contract)
        f = open(full_result_path, "w+")
        if f:
            f.write(content)
            f.close()