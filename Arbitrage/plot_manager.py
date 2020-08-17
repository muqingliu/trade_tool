
import math
import numpy as np
import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import datetime
from matplotlib.dates import AutoDateLocator, DateFormatter
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import matplotlib.path as path

COLOR = ['black', 'red', 'orange', 'green',  'blue', 'purple', 'tan', 'brown', 'gray']

class class_plot_manager(object):
    def __init__(this):
        this.figure_num = 0
        this.color_index = -1

    def get_color(this):
        this.color_index += 1
        if this.color_index == len(COLOR): this.color_index = 0
        return COLOR[this.color_index]

    def create_figure(this, figure_size = None): #创建新图表
        this.figure_num += 1
        if figure_size is None:
            plt.figure(this.figure_num)
        else:
            plt.figure(this.figure_num, figsize=figure_size, dpi=72, frameon=(this.figure_num ,this.figure_num))


    def plot_normal_distribution2(this, df_datas, mu = None, sigma = None, is_testCase = False): #正态分布图
        this.create_figure()

        if mu is None: mu = np.mean(df_datas['point'])
        if sigma is None: sigma = np.std(df_datas['point'])

        num_bins = 50
        # the histogram of the data
        n, bins, patches = plt.hist(df_datas['point'], num_bins, normed=1, facecolor='blue', alpha=0.5, cumulative=True)
        # add a 'best fit' line
        y = mlab.normpdf(bins, mu, sigma)
        plt.plot(bins, y, 'r--')
        plt.xlabel('Smarts')
        plt.ylabel('Probability')
        plt.title(r'Histogram of IQ: $\mu=100$, $\sigma=15$')

        # Tweak spacing to prevent clipping of ylabel
        plt.subplots_adjust(left=0.15)
        plt.show()

    def plot_normal_distribution(this, df_datas, mu = None, sigma = None, is_testCase = False): #正态分布图
        this.create_figure()

        if mu is None: mu = np.mean(df_datas['point'])
        if sigma is None: sigma = np.std(df_datas['point'])

        # 条形柱数量
        max_val = float(df_datas.max())
        min_val = float(df_datas.min())
        num_bins = int(np.sqrt(df_datas['point'].count()))
        interval = (max_val - min_val)/float(num_bins)
        y_datas = []
        down_boundary = min_val - interval
        x_datas = [down_boundary]
        maxCounter = 0
        for num_index in range(num_bins):
            up_boundary = down_boundary + interval
            counter = int(df_datas[(df_datas['point']>down_boundary)&(df_datas['point']<=up_boundary)].count())
            if counter > maxCounter:maxCounter = counter
            y_datas.append(counter)
            x_datas.append(up_boundary)
            down_boundary += interval

        #画直方图
        ax = plt.gca()
        left = np.array(x_datas[:-1])
        right = np.array(x_datas[1:])
        bottom = np.zeros(len(left))
        top = y_datas
        XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T
        barpath = path.Path.make_compound_path_from_polys(XY)
        patch = patches.PathPatch(
            barpath, facecolor='blue', edgecolor='gray', alpha=0.8)
        ax.add_patch(patch)
        ax.set_xlim(left[0], right[-1])
        ax.set_ylim(0, maxCounter + maxCounter/10)

        ##画标准正态分布曲线
        n, bins = np.histogram(df_datas, 50)

        # from scipy import special
        # print(special.erf(bins[0:10]))

        y = mlab.normpdf(bins, mu, sigma)
        par1 = plt.twinx()
        plt.plot(bins, y, 'r--')

        if is_testCase: #测试用例
            cmp_x_datas = [-568.0, -402.0, -236.0, -70.0, 96.0]
            cmp_y_datas = [1, 3, 7, 10]
            if cmp(x_datas, cmp_x_datas) !=0 or cmp(y_datas, cmp_y_datas)!=0:
                raise ValueError('error function plot_normal_distribution')


    def plot_parallel_lines(this, x_parallel_lines, line_length): #画平行线
        if x_parallel_lines is None or line_length ==0: return
        for x_parallel_line in x_parallel_lines:
            plt.plot([0, line_length], [x_parallel_line, x_parallel_line])


    def plot_single_slice_line(this, file_name, df_datas, slice_time, x_parallel_lines = None, line_iLoc = None):
        df_slice_datas = df_datas[slice_time[0]:slice_time[1]]

        alone_figure = False
        if line_iLoc is None:
            this.create_figure(figure_size = (20,10))
            alone_figure = True
            line_iLoc = 0

        list_datestamps = list(df_slice_datas.index)
        length = len(df_slice_datas)
        plt.plot(np.arange(line_iLoc, line_iLoc + length),df_slice_datas['point'], this.get_color(), label = '$%s-%s$'%(str(list_datestamps[0].to_period('D')), str(list_datestamps[-1].to_period('D'))))

        if x_parallel_lines is not None: this.plot_parallel_lines(x_parallel_lines, length)

        if alone_figure:
            this.set_xticks(list_datestamps)
            plt.xlim(0,length)
            plt.grid(True) #画网格
            plt.xlabel("Time(s)")
            plt.ylabel("Point")
            plt.legend()

            plt.title(file_name)

        return line_iLoc + length



    def plot_sectional_curve(this, file_name, df_datas, slice_times, x_parallel_lines = None, multiple_figure = True): #画分段曲线

        if multiple_figure:
            for slice_time in slice_times:
                this.plot_single_slice_line(file_name, df_datas, slice_time, x_parallel_lines)
        else:

            this.create_figure(figure_size = (20,10))

            #绘制分段曲线
            iLoc = 0
            for slice_time in slice_times:
                iLoc = this.plot_single_slice_line(file_name, df_datas, slice_time, x_parallel_lines, iLoc)


            data_count = df_datas['point'].count()  #数据个数
            #画平行于X轴的直线
            this.plot_parallel_lines(x_parallel_lines, data_count)

            this.set_xticks(list(df_datas.index), 60)

            plt.xlim(0,len(df_datas))

            max_val = max(df_datas['point'].max(), max(x_parallel_lines))
            min_val = min(df_datas['point'].min(), min(x_parallel_lines))
            plt.ylim(min_val-(max_val - min_val)/10, max_val+ (max_val - min_val)/10) #设置Y轴边界值

            plt.grid(True) #画网格
            plt.xlabel("Time(s)")
            plt.ylabel("Point")
            plt.legend(ncol = len(slice_times)/3)

            plt.title(file_name)


    def plot_bar(this, df_records): #柱形图
        this.create_figure()

        df_datas = df_records[df_records['profit'].notnull()]
        df_datas = df_datas['profit']
        length = len(df_datas)
        ax = plt.gca()
        left = np.arange(0,length)
        right = np.arange(1,length+1)
        bottom = np.zeros(length)
        top = list(df_datas.values)
        XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T
        barpath = path.Path.make_compound_path_from_polys(XY)
        patch = patches.PathPatch(
            barpath, facecolor='green', edgecolor='gray', alpha=0.8)
        ax.add_patch(patch)

        ax.set_xlim(1, length)
        max = df_datas.max()
        min = df_datas.min()
        ax.set_ylim(min - abs(min)/10, max + abs(max)/10)

        list_datestamps = list(df_datas.index)
        this.set_xticks(list_datestamps, 15, 10)



    def set_xticks(this, list_datestamps, rotation = 15, x_tick_interval = 30):
        ax = plt.gca()
        length = len(list_datestamps)
        #plt.xticks(np.arange(0, len(list_datestamps)), list_datestamps, fontsize = 10)
        def x_ticker(x, pos=None):
            thisind = int(x)
            return list_datestamps[thisind]
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(x_ticker))

        #设置X轴刻度间
        tick_interval = 1
        if length>x_tick_interval:tick_interval = length/x_tick_interval
        ax.set_xticks(range(0,length, tick_interval))
        xlabels = ax.get_xticklabels()

        for xl in xlabels:
            xl.set_rotation(rotation) #把x轴上的label旋转15度,以免太密集时有重叠
        pass


    def plot_cumsum_profit_curve(this, df_records): #累计收益点数点状曲线图
        this.create_figure()

        df_records = df_records[df_records['profit'].notnull()]
        df_records = df_records.apply(np.cumsum)  #数值累加

        list_datestamps = list(df_records.index)
        length = len(list_datestamps)
        plt.plot(np.arange(0, length), list(df_records['profit']), 'r.-')


        this.set_xticks(list_datestamps, 15, 10)
        plt.xlim(0,length)
        plt.title('cumsum profit')



    def plot_trade_point(this, df_records, wait_change_period, x_parallel_lines = None):  #开仓、平仓点状图
        this.create_figure(figure_size = (20,10))
        ax = plt.gca()

        list_datestamps = list(df_records.index)

        df_records = df_records.reset_index()  #设置新的索引

        #画平行于X轴的直线
        if x_parallel_lines:this.plot_parallel_lines(x_parallel_lines, len(df_records))

        df_open_datas = df_records[df_records['profit'].isnull()]  #开仓数据
        df_wait_change_period_open_datas = df_open_datas[df_open_datas['index'].isin(wait_change_period)]
        ax.plot(list(df_wait_change_period_open_datas.index), list(df_wait_change_period_open_datas['point']),'8', label ='wait_change_period', **dict(color='black', markersize=10))

        df_not_change_period_open_datas = df_open_datas[df_open_datas['index'].isin(list(set(list(df_open_datas['index'])).difference(set(wait_change_period))))]
        open_point_marker_style = dict(color='cornflowerblue', markersize=10)
        ax.plot(list(df_not_change_period_open_datas.index), list(df_not_change_period_open_datas['point']),'8', label ='open', **open_point_marker_style)

        df_close_datas = df_records[df_records['profit'].notnull()]  #平仓数据

        close_win_point_marker_style = dict(color='red', markersize=10)
        df_close_win_datas = df_close_datas[df_close_datas['profit']>=0]  #平仓盈利数据
        ax.plot(list(df_close_win_datas.index), list(df_close_win_datas['point']),'d', label ='close_win', **close_win_point_marker_style)

        close_loss_point_marker_style = dict(color='green', markersize=10)
        df_close_loss_datas = df_close_datas[df_close_datas['profit']<0]  #平仓亏损数据
        ax.plot(list(df_close_loss_datas.index), list(df_close_loss_datas['point']),'d', label ='close_loss', **close_loss_point_marker_style)

        ax.set_xlim(0, len(df_records))

        y_max = df_records['point'].max()
        y_min = df_records['point'].min()
        if x_parallel_lines:
            y_max = max(y_max, max(x_parallel_lines))
            y_min = min(y_min, min(x_parallel_lines))
        ax.set_ylim(y_min - abs(y_min)/10, y_max + abs(y_max)/5)

        plt.legend(ncol = 4)
        this.set_xticks(list_datestamps)


    def show(this):#要画的图片都画好后，统一调用
        plt.show()


    def save(this, save_path):  #保存图片
        plt.savefig(save_path, format='png')

