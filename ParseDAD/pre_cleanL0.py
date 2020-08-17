import re
import os
import sys

def read_origin_data(file_name):
    list_data = []
    f = open(file_name, "rt")
    if f:
        l = f.readline()
        while l:
            try:
                ma = re.findall("(\d+)/(\d+)/(\d+)-(\d+):(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+(?:\.\d+){0,1})$", l)
                if ma:
                    y = int(ma[0][0])
                    m = int(ma[0][1])
                    d = int(ma[0][2])
                    h = int(ma[0][3])
                    mm= int(ma[0][4])
                    _open = float(ma[0][5])
                    _hith = float(ma[0][6])
                    _low  = float(ma[0][7])
                    _close= float(ma[0][8])
                    _num  = float(ma[0][9])
                    list_data.append([y,m,d,h,mm,_open,_hith,_low,_close,_num,0])
            except Exception as  e:
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


def process(contract_temp):
    input_path = "."
    output_path = 'output'

    if len(sys.argv) > 1:# 拖曳的时候获取数据文件路径与名字
        file_path = sys.argv[1]
        input_path, input_file_name = os.path.split(file_path)
        ma = re.match("(\w+)L0\.txt", input_file_name)
        contract_temp = ma.group(1)

    read_data_file_name = "%s/input/%sL0.txt" % (input_path, contract_temp)
    list_data = read_origin_data(read_data_file_name)

    read_day_file_name = "%s/gaps/%sgaps.txt" % (input_path, contract_temp)
    if(not os.path.exists(read_day_file_name)):
        print("%s gaps file not exits" % contract_temp)
        return

    list_day = read_season_day(read_day_file_name)

    base_path = os.getcwd()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    target_file_name =  "%s/%sL0.txt" % (output_path, contract_temp)

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
            data_str = "%d/%02d/%02d-%02d:%02d\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (data[0], data[1], data[2], data[3],
                                                                                   data[4], data[5], data[6], data[7],
                                                                                   data[8], data[9], data[10])
            f.write(data_str)

        f.close()


def search_input_files(rootdir):
    import os
    files = []
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            (filepath, tempfilename) = os.path.split(filename)
            shotname, extension = os.path.splitext(tempfilename)
            files.append(shotname)
    return files


if __name__ == '__main__':
    try:
        # cs = ["a","ag","al","au","bb","bu","CF","c","cs","cu","FG","hc","i","jd","j","jm","l","MA","m","OI","p","pp","RM","SR","TF","ZC","zn"]
        # cs = ["y", "pp", "cs", "v", "zn", "sn", "ZC", "SM", "SF", "RS", "OI", "CF"]
        cs = ["rb","ru"]

        if len(cs) == 0:
            files = search_input_files("input")
            cs = [c[:-2] for c in files]
        for c in cs:
            process(c)
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
