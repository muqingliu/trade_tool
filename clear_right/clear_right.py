import re
import os
import sys
import copy
import subprocess
import ConfigParser

class SystemConfig(object):
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)
        
        self.continuous_data=ini_parser.get("main", "continuous_data")
        self.gaps_data=ini_parser.get("main", "gaps_data")
        self.after_complex_data=ini_parser.get("main", "after_complex_data")
        self.former_complex_data=ini_parser.get("main", "former_complex_data")
        self.last_exe = ini_parser.get("main", "last_exe")

def read_origin_data(file_name):
    list_data = []
    f = open(file_name, "rt")
    if f:
        l = f.readline()
        while l:
            try:
                ma = re.findall(
                    "(\d+)/(\d+)/(\d+)-(\d+):(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+(?:\.\d+){0,1})$", l)
                if ma:
                    y = int(ma[0][0])
                    m = int(ma[0][1])
                    d = int(ma[0][2])
                    h = int(ma[0][3])
                    mm = int(ma[0][4])
                    _open = float(ma[0][5])
                    _hith = float(ma[0][6])
                    _low = float(ma[0][7])
                    _close = float(ma[0][8])
                    _num = float(ma[0][9])
                    list_data.append(
                        [y, m, d, h, mm, _open, _hith, _low, _close, _num, 0])
            except Exception as e:
                print(e)
            l = f.readline()
        f.close()

    return list_data


def read_season_day(file_name):
    list_day = []
    f = open(file_name, "rt")
    if f:
        l = f.readline()
        while l:
            try:
                ma = re.findall("(\d+)/(\d+)/(\d+)-(\d+):(\d+)", l)
                if ma:
                    y = int(ma[0][0])
                    m = int(ma[0][1])
                    d = int(ma[0][2])
                    h = int(ma[0][3])
                    mm = int(ma[0][4])
                    list_day.append([y, m, d, h, mm])
            except Exception as e:
                print(e)
            l = f.readline()
        f.close()

    return list_day


def produce_after_complex_data(after_complex_data_dir, contract, list_data, list_day):
    target_file_name = "%s\\%sL0.txt" % (after_complex_data_dir, contract)
    f = open(target_file_name, "wt+")
    if f:
        last_close = 0
        diff = 0
        for data in list_data:
            for day in list_day:
                if data[0] == day[0] and data[1] == day[1] and data[2] == day[2] and data[3] == day[3] and data[4] == day[4]:
                    diff = data[5] - last_close

            data[5] = data[5] - diff
            data[6] = data[6] - diff
            data[7] = data[7] - diff
            data[8] = data[8] - diff
            data[10] = diff

            last_close = data[8]

            data_str = "%d/%02d/%02d-%02d:%02d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\n" %\
                (data[0], data[1], data[2], data[3],
                 data[4], data[5], data[6], data[7],
                 data[8], data[9], data[10])
            f.write(data_str)

        f.close()


def produce_before_complex_data(former_complex_data_dir, contract, list_data, list_day):
    target_file_name = "%s\\%sL0.txt" % (former_complex_data_dir, contract)
    f = open(target_file_name, "wt+")
    if f:
        list_data_len = len(list_data)
        list_day_len = len(list_day)
        next_open = list_data[list_data_len-1][5]
        diff = 0
        for i in range(list_data_len-1, 0, -1):
            for j in range(list_day_len-1, -1, -1):
                if list_data[i][0] == list_day[j][0] and list_data[i][1] == list_day[j][1] and list_data[i][2] == list_day[j][2] and list_data[i][3] == list_day[j][3] and list_data[i][4] == list_day[j][4]:
                    diff = next_open - list_data[i-1][8]
            list_data[i-1][5] = list_data[i-1][5] + diff
            list_data[i-1][6] = list_data[i-1][6] + diff
            list_data[i-1][7] = list_data[i-1][7] + diff
            list_data[i-1][8] = list_data[i-1][8] + diff
            list_data[i-1][10]= -diff

            next_open = list_data[i-1][5]


        for data in list_data:
            data_str = "%d/%02d/%02d-%02d:%02d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\n" % (data[0], data[1], data[2], data[3],
                                                                                   data[4], data[5], data[6], data[7],
                                                                                   data[8], data[9], data[10])
            f.write(data_str)

        f.close()


def search_continuous_data_file(continuous_data_dir):
    file_dic = {}
    for root,dirs,files in os.walk(continuous_data_dir):
        for file in files:
            index = file.find("L0")
            if -1 == index:
                continue

            contract = file[0:index]

            file_path = os.path.join(root, file)
            file_dic[contract] = file_path

    return file_dic


def search_gaps_data_file(gaps_data_dir):
    file_dic = {}
    for root,dirs,files in os.walk(gaps_data_dir):
        for file in files:
            index = file.find("gaps")
            if -1 == index:
                continue

            contract = file[0:index]

            file_path = os.path.join(root, file)
            file_dic[contract] = file_path

    return file_dic


def process():
    cur_path = os.path.split(sys.argv[0])[0]
    sys_full_path = os.path.join(cur_path, "system.ini")
    sys_info = SystemConfig(sys_full_path)

    continuous_data_paths = search_continuous_data_file(sys_info.continuous_data)
    gaps_paths = search_gaps_data_file(sys_info.gaps_data)
    for contract in continuous_data_paths.keys():
        if not gaps_paths.has_key(contract):
            continue

        continuous_data_path = continuous_data_paths[contract]
        gaps_path = gaps_paths[contract]

        list_data = read_origin_data(continuous_data_path)
        list_day = read_season_day(gaps_path)

        after_list_data = copy.deepcopy(list_data)
        after_list_day = copy.deepcopy(list_day)
        former_list_data = copy.deepcopy(list_data)
        former_list_day = copy.deepcopy(list_day)

        produce_after_complex_data(sys_info.after_complex_data, contract, after_list_data, after_list_day)
        produce_before_complex_data(sys_info.former_complex_data, contract, former_list_data, former_list_day)

    if len(sys_info.last_exe) > 0 and os.path.exists(sys_info.last_exe) and os.path.isfile(sys_info.last_exe) \
        and os.path.splitext(sys_info.last_exe)[1] == '.exe':
        print sys_info.last_exe
        subprocess.Popen(sys_info.last_exe)


if __name__ == '__main__':
    try:
        process()
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
