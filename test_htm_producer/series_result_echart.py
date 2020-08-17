#对齐日期，
align_date = 99999999

template ="""
<!DOCTYPE html>
<head>
    <meta charset="utf-8">
    <title><<!!title>></title>
</head>
<body>
    <!-- 为ECharts准备一个具备大小（宽高）的Dom -->
    <div id="profit_div" style=\"height:700px\"></div>
    <!-- ECharts单文件引入 -->
    <script src="echarts.js"></script>
    <script src="common_echart.js"></script>
    <script type="text/javascript">
        <<!!chart>>
    </script>
</body>
"""


import json
import re
import os
import time


def find_test_result_file(rootdir, key_str):
    test_tool_dirs = [rootdir]

    timestamp = time.time()
    st_time = time.gmtime(timestamp)

    policy = ""
    map_test_file = {}

    map_contract_log_full_path = {}
    for test_tool_dir in test_tool_dirs:
        test_tool_full_path = os.path.join(rootdir,test_tool_dir)
        test_log_full_path = "%s\\log\\%04d-%d" % (test_tool_full_path,st_time.tm_year,st_time.tm_mon)

        for parent,dirnames,filenames in os.walk(test_log_full_path):
            for dirname in dirnames:
                contract = dirname
                contract_log_full_path = "%s\\%s\\%s" % (test_log_full_path, contract, contract)
                map_contract_log_full_path[contract] = contract_log_full_path

    for contract in map_contract_log_full_path.keys():
        contract_log_full_path = map_contract_log_full_path[contract]
        for parent,dirnames,filenames in os.walk(contract_log_full_path):
            if not map_test_file.has_key(contract):
                map_test_file[contract] = {}

            for filename in filenames:
                file_word_list = filename.split('_')
                key_index = filename.find(key_str)
                if key_index >= 0 and file_word_list[0] != contract:
                    point_index = filename.find(".")
                    param_str = filename[key_index+len(key_str)+1:point_index]

                    if len(policy) == 0:
                        policy = filename[0:key_index-1]

                    full_file_path = os.path.join(parent,filename)
                    map_test_file[contract][param_str] = full_file_path

    return (policy,map_test_file)


def get_web_path(rootdir, policy, contract, key_str):
    full_path = os.path.join(rootdir,policy)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    full_path = "%s\\%s_%s.htm" % (full_path, contract, key_str)
    return full_path


def parse_time(time):
    time_set = []
    m = re.findall("(\d{6})-(\d{2}):(\d{2})",time)
    if m:
        arrs = m[0]
        year = 2000 + int(arrs[0]) / 10000
        month = int(arrs[0]) / 100 % 100
        day = int(arrs[0]) % 100
        hour = 9
        minute = 1
        time_set.append(year)
        time_set.append(month)
        time_set.append(day)
        time_set.append(hour)
        time_set.append(minute)
    return time_set


def make_time(time):
    m = re.findall("(\d{6})-(\d{2}):(\d{2})",time)
    if m:
        arrs = m[0]
        result = '20%s/%s/%s-15:00' % (arrs[0][0:2], arrs[0][2:4], arrs[0][4:6])
        return result
    return ""


def read_margin(filename):
    datas = [[],[]]
    with open(filename, 'rb') as f:
        align_profit = 0
        line = f.readline()
        while line:
            eles = line.split('\t')
            time = make_time(eles[0])
            profit = float(eles[1])

            time_set = parse_time(eles[0])
            date = time_set[0] * 10000 + time_set[1] * 100 + time_set[2]
            if date >= align_date:
                if align_profit == 0:
                    align_profit = profit

            datas[0].append(time)
            datas[1].append([time, profit])
            line = f.readline()

    for data_pair in datas[1]:
        data_pair[1] = data_pair[1] - align_profit

    return datas


def read_close_equity(filename):
    datas = [[],[]]
    with open(filename, 'rb') as f:
        align_close_equity = 0
        line = f.readline()
        while line:
            eles = line.split('\t')
            time = make_time(eles[0])
            close_equity = float(eles[2])

            time_set = parse_time(eles[0])
            date = time_set[0] * 10000 + time_set[1] * 100 + time_set[2]
            if date >= align_date:
                if align_close_equity == 0:
                    align_close_equity = close_equity

            datas[0].append(time)
            datas[1].append([time, close_equity])
            line = f.readline()

    for data_pair in datas[1]:
        data_pair[1] = data_pair[1] - align_close_equity

    return datas


def merge_datas(time_set, contract_all_datas, param_str, datas):
    times = datas[0]
    if len(time_set) == 0:
        time_set.extend(times)

    size = len(datas[1])
    last_profit = datas[1][size - 1][1]
    if last_profit == 0:
        return

    tar_index = -1
    for index,all_data_pairs in enumerate(contract_all_datas):
        all_data_size = len(all_data_pairs[1])
        all_last_profit = all_data_pairs[1][all_data_size - 1][1]
        if last_profit > all_last_profit:
            tar_index = index
            break

    if tar_index >= 0:
        contract_all_datas.insert(tar_index, (param_str, datas[1]))
    else:
        contract_all_datas.append((param_str, datas[1]))


def create_chart_str(contract, time_set, y_axis_name, contract_all_datas):
    times = ["'" +e + "'" for e in time_set]

    begin_idx = 0
    end_idx = -1

    timesstr = (',').join(times[begin_idx:end_idx])

    series = []
    for items in contract_all_datas:
        series_profit = {'name':items[0],
                    'type':'line',
                    'data':items[1][0:]
                    }

        series.append(series_profit)

    series_names_str = (',').join(["'" + serie['name'] + "'" for serie in series])

    chart_str = "chart_draw_line(echarts, \"profit_div\", \"%s\", [%s], \"%s\", [%s], %s);\n" \
                % (contract, series_names_str, y_axis_name, timesstr, json.dumps(series))
    return chart_str


def create_result_web(web_path, contract, time_set, y_axis_name, contract_all_datas):
    chart_str = create_chart_str(contract, time_set, y_axis_name, contract_all_datas)

    content = template.replace('<<!!title>>', contract)
    content = content.replace('<<!!chart>>', chart_str)

    f = open(web_path, "w+")
    if f:
        f.write(content)
        f.close()


if __name__ == '__main__':
    main()
