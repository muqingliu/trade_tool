import os
import re
import math
import traceback
BASE_EQUITY = 1


def search_margin_files(rootdir):
    margin_files = []
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if filename.find("margin") != -1:
                fullname = os.path.join(parent, filename)
                margin_files.append(fullname)
            # _path,_file=os.path.split(fullname)

            # print _file.find("equity")
            # print filename
    return margin_files


def process_files(files):
    files_datas = {}
    for _path in files:
        datas = []
        with open(_path, 'rb') as f:
            index = 0
            l = f.readline()
            while l:
                eles = l.split('\t')
                equity = float(eles[1])
                date = eles[0].split('-')[0]
                margin_rate = float(eles[4])

                datas.append((date, equity, margin_rate))

                index = index + 1
                l = f.readline()

        if len(datas) > 0:
            evalute = process_datas(datas)
            _p, _f = os.path.split(_path)

            new_file_name = "%f_%s" % (evalute, _f)
            if evalute < 0:
                new_file_name = "r %f_%s" % (-evalute, _f)

            new_fullname = os.path.join(_p, new_file_name)
            os.rename(_path, new_fullname)
            files_datas[new_fullname] = datas

            _f_equity = find_equity_file(_p, _f)
            if len(_f_equity) > 0:
                new_equity_file_name = "%f_%s" % (evalute, _f_equity)
                if evalute < 0:
                    new_equity_file_name = "r %f_%s" % (-evalute, _f_equity)

                _path_equity = os.path.join(_p, _f_equity)
                _path_new_equity = os.path.join(_p, new_equity_file_name)
                os.rename(_path_equity, _path_new_equity)

    return files_datas

def find_equity_file(path, file):
    for parent, dirnames, filenames in os.walk(path):
        for filename in filenames:
            index = filename.find("equity")
            if index != -1:
                temp_filename = filename.replace("equity", "margin")
                if cmp(temp_filename, file) == 0:
                    return filename

    return ""


def process_datas(datas):
    count = len(datas)
    max_quity = datas[count - 1]
    slope = float(max_quity[1]) / count  # 求斜率

    index = 0
    square = 0
    for _data in datas:
        _date, _equity = _data[0], float(_data[1])

        _cur_slope = slope * (index + 1)

        _p1 = _equity - BASE_EQUITY
        _p2 = _cur_slope

        square = square + (_p1 - _p2) * (_p1 - _p2)

        index = index + 1

    square = math.sqrt(square)

    eva = slope * slope / square * 100000
    if slope < 0:
        eva = -eva
    return eva


def main():
    margin_files = search_margin_files("./equity")

    process_files(margin_files)


if __name__ == '__main__':

    main()
