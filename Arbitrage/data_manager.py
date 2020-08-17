
import os
import re
import pandas as pd
import numpy as np

class class_data_manager(object):
    def __init__(this, dir_path, time_slice_cfg_path):
        this.root_path = os.getcwd()

        this.file_data_slice_times = {}
        this.load_time_slice_datas(time_slice_cfg_path)

        this.datas = {}
        this.load_data(dir_path)
        this.trade_datestamps = None
        this.mu = None
        this.sigma = None

    def load_data(this, dir_path):
        dir_path = os.path.join(this.root_path, dir_path)

        if not os.path.exists(dir_path):
            raise ValueError("folder:%s is not exist" % dir_path)
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.find('same') == -1  and file.find('diff') == -1: continue
                if this.datas.has_key(file):continue

                file_path = os.path.join(root, file)
                file_obj = open(file_path)
                dates = []
                values =[]

                try:
                    for line in file_obj.readlines():
                        ma = re.match("(.*)\s(-?\d+.?\d*)$", line)
                        if ma is None:continue
                        ma = ma.groups(0)
                        dates.append(ma[0])
                        values.append(float(ma[1]))

                except IOError:
                    file_obj.close()
                    raise ValueError("can not read file: %s" % file_path)

                df = pd.DataFrame(values, index=pd.to_datetime(dates), columns=['point'])
                this.datas[file] = df


    def load_time_slice_datas(this, time_slice_cfg_path): #读取每个价差数据文件的每段数据的起始、末尾时间
        time_slice_cfg_path = os.path.join(this.root_path, time_slice_cfg_path)

        if not os.path.exists(time_slice_cfg_path):
            raise ValueError("folder:%s is not exist" % time_slice_cfg_path)
        try:
            file_obj = open(time_slice_cfg_path)
            for line in file_obj.readlines():
                ma = re.match("([^\s]+)\s([^\s]+)\s([^\s]+)", line)
                if ma is None:continue
                file_name, beg_time, end_time = ma.groups(0)
                if not this.file_data_slice_times.has_key(file_name):this.file_data_slice_times[file_name] = []
                this.file_data_slice_times[file_name].append((pd.to_datetime(beg_time), pd.to_datetime(end_time)))
        except IOError:
             file_obj.close()
             raise ValueError("can not read file: %s" % time_slice_cfg_path)

    def get_all_datas(this):#获取所有数据
        if len(this.datas) == 0: return None
        return pd.concat(this.datas.values())

    def get_file_datas(this, file_name): #获取某个文件中的所有数据
        if not this.datas.has_key(file_name): return None
        return this.datas[file_name]

    def get_data_file_names(this): #获取所有数据文件名称
        return this.datas.keys()

    def get_file_slice_times(this, file_name):
        if not this.file_data_slice_times.has_key(file_name):return None
        return this.file_data_slice_times[file_name]

    def get_file_slice_datas(this, file_name, beg_time, end_time):
        if not this.datas.has_key(file_name): return None
        return this.datas[file_name][beg_time:end_time]

    def get_point(this, file_name, datestamp):
        df_datas = this.get_file_datas(file_name)
        if df_datas is None: return None
        return df_datas.at[datestamp,'point']


    def get_belong_slice_time(this, file_name, datestamp): #当前日期属于哪个时间片段内
        slice_times = this.get_file_slice_times(file_name)
        if slice_times is None: return None
        for slice_time in slice_times:
            if datestamp >=slice_time[0] and datestamp <=slice_time[1]: return slice_time
        return None

    def is_delivery_day(this, file_name, datestamp):  #是否是交割日
        slice_time = this.get_belong_slice_time(file_name, datestamp)
        if slice_time is None: return False
        if slice_time[1] == datestamp: return True
        return False

    def get_trade_datestamps(this):
        if this.trade_datestamps is None:
            df_all_datas = this.get_all_datas()
            this.trade_datestamps = df_all_datas.sort().index.unique()
        return this.trade_datestamps

    def get_trade_datestamps_by_id(this, id): #某个合约的交易时间集合
        df_id_datas = this.get_file_datas(id)
        if df_id_datas is None: return None
        return df_id_datas.sort().index.unique()

    def get_interval_days_befor_delivery(this, file_name, datestamp):
        slice_time = this.get_belong_slice_time(file_name, datestamp)
        if slice_time is None: return 0
        list_trade_datestamps = list(this.get_trade_datestamps())
        interval_days = list_trade_datestamps.index(slice_time[1]) - list_trade_datestamps.index(datestamp)

    def get_mu(this):
        if this.mu is None:
            df_datas = this.get_all_datas()
            this.mu = np.mean(df_datas['point'])
        return this.mu

    def get_sigma(this):
        if this.sigma is None:
            df_datas = this.get_all_datas()
            this.sigma = np.std(df_datas['point'])
        return this.sigma


    #def get_file_all_slice_datas(this, file_name): #获取一个文件中的所有分段数据
    #    all_datas = []
    #    for beg_time, end_time in this.get_file_slice_times(file_name):
    #        datas = this.get_file_slice_datas(file_name, beg_time, end_time)
    #        all_datas.append(datas)
    #    return all_datas


