#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import common

def get_vars():
    vars = []
    ini_file = open("calc_spread.ini", "rt")
    if ini_file:
        line = ini_file.readline()
        line_num = 0
        while line:
            line_num += 1
            try:
                if not re.match("^[#]", line): 
                    ma = re.findall("(\w+)[,-](\w+)$", line)
                    if ma:
                        var_1 = ma[0][0]
                        var_2 = ma[0][1]
                        vars.append((var_1, var_2)) 
                    else:
                        print "line %d not match!" % (line_num)

            except Exception, e:
                print e
            line = ini_file.readline()
        ini_file.close()
    return vars


def read_var(var_name):
    group = {}
    file_name = "day_data/%sl0.txt" % var_name
    datas = common.read_origin_data(file_name)

    for data in datas:
        time = int("%d%s%s" % (int(data[0]), data[1], data[2]))
        group[time] = data[8]
    return group

def prepare_data(vars):
    for var in vars:
        group1 = read_var(var[0])
        group2 = read_var(var[1])

        print "%s %d : %s %d" %(var[0], len(group1), var[1], len(group2))
        calc_spread(var[0], var[1], group1, group2)

def calc_spread(var1, var2, group1, group2):
    average = 0
    lines = []
    for time, data1 in group1.items():
        data2 = group2.get(time)
        if not data2: continue

        data1 = float(data1)
        data2 = float(data2)
        average += data1 - data2

        line = "%d\t%d\t%.2f" % (time, data1-data2, data1/data2)
        lines.append(line)

    line_num = len(lines)
    if 0 != line_num:
        average = average / line_num

    lines.sort()

    out_file_name = "spread_%s-%s.txt" % (var1, var2)
    out_file = open(out_file_name, "w")

    for line in lines:
        line += "\t%.2f\n" % (average)
        out_file.write(line)
    out_file.close()


def main():
    vars = get_vars()
    prepare_data(vars)
    

if __name__ == '__main__': 
	main()
