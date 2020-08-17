
import os,re
import matplotlib.pyplot as plt
import numpy as np
import math
from functools import cmp_to_key

def get_sort_margin_params(rootdir):
    margin_part_files = {}
    for parent,dirnames,filenames in os.walk(rootdir): 
        for filename in filenames:
            if filename.find("margin") != -1:
                ma = re.findall("([r ]*)(\d+\.\d+)_(\w+)\.log", filename)
                if len(ma) == 0: continue
                evalute = float(ma[0][1])
                file_name = ma[0][2]
                if evalute == 0: continue #该值为零就不绘制
                if (ma[0][0] == 'r'):
                    evalute = -evalute
                margin_part_files[file_name] = evalute

    margin_part_files= sorted(margin_part_files.items(), key=lambda d:d[1], reverse = True)
    sort_params = []
    for margin_part_file in margin_part_files:
        vals = margin_part_file[0].split('_')
        sort_params.append((int(vals[-1]), int(vals[-2])))
        #print vals
    return sort_params


#def get_gradient_colors():#获得渐变颜色  256种颜色
#    g = 15
#    colors = []
#    while g >=0:
#        b = 0
#        while b <= 15:
#            color = (1,g/15.00,b/15.00)
#            colors.append(color)
#            b = b+1
#            print color
#        g=g-1
#    return colors

def get_gradient_colors(threshold=100):  #生成的渐变颜色数量为2*threshold-1  由红-黄-绿
    index = 1
    colors = []
    while index < 2*threshold:
        i=0
        g = min(255, (index*1.0/threshold*255))*1
        r = max(0, min(255, (2 - index * 1.0 / threshold) * 255)) * 1
        color = (r/255.0,g/255.0,0)
        colors.append(color)
        index += 1
    return colors



def sort_scatter_diagram(sort_params, name):
    plt.figure(figsize=(10,5))
   
    gradient_colors = get_gradient_colors(math.ceil(len(sort_params)/2.0)+1)
    index = 0
    x_max = 0
    y_max = 0 
    for param in sort_params:
        x_max = max(x_max, param[0])
        y_max = max(y_max, param[1])
        plt.plot(param[0],param[1], 'd',color = gradient_colors[index])
        index += 1

    plt.xticks(np.arange(0, x_max+5,5))
    plt.yticks(np.arange(0, y_max+5,5))
    plt.xlabel("lost_day_param")
    plt.ylabel("break_day_param")
    plt.xlim(0, x_max + 5)
    plt.ylim(0, y_max + 5)
    plt.grid()
    plt.title(name)
    plt.savefig('%s.png'%name)
    plt.show()



if __name__ == '__main__':  
    #plt.figure(figsize=(10,5))
    #gradient_colors = get_gradient_colors()
    #len = len(gradient_colors)
    #for index in range(0,len):
    #    plt.plot(index,index, 'd',color = gradient_colors[index])
    #plt.show()
    #rootdir = os.path.curdir
    #for parent,dirnames,filenames in os.walk(rootdir):
    #    for dirname in dirnames:
    #        #margin_files = equity_sort.search_margin_files(dirname)
    #        #equity_sort.process_files(margin_files)
    
    #        sort_params = get_sort_margin_params(dirname)
    #        sort_scatter_diagram(sort_params, dirname)

    dirname = 'equity'
    #margin_files = equity_sort.search_margin_files(dirname)
    #equity_sort.process_files(margin_files)
    
    sort_params = get_sort_margin_params(dirname)
    sort_scatter_diagram(sort_params, dirname)
