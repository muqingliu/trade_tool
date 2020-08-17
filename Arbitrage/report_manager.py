import pandas as pd
import log

LOG_SUMMARY_REPORT = 'summary_report'


class class_report_mgr(object):
    def __init__(this):
        this.df_records = pd.DataFrame(columns= ['id','point','number','dir','profit']) #dir=1开仓  dir=0 平仓

    def add_up(this, id, is_testCase = False):
        open_time = this.get_open_times(id)
        win_time, win_point = this.get_win_situation(id)
        loss_time, loss_point = this.get_loss_situation(id)
        win_ratio = win_time/float(win_time + loss_time)  #胜率

        win_loss_ratio = 0 #盈亏比
        if abs(loss_point)*win_time !=0:
            win_loss_ratio = (win_point*loss_time)/float(abs(loss_point)*win_time)

        max_win_point = this.get_max_win_point(id)
        max_loss_point = this.get_max_loss_point(id)

        df_index = this.df_records['profit'].notnull()
        if id is not None:
            df_index = df_index & (this.df_records['id'] == id)
        df_datas = this.df_records[df_index]

        total_profit = 0
        max_total_profit = -99999
        max_retrace = 0
        max_constant_win_time = 0  #最大连胜次数
        max_constant_win_point = 0  #最大连胜点数
        max_constant_loss_time = 0   #最大连亏次数
        max_constant_loss_point = 0  #最大连亏点数
        constant_win_time = 0
        constant_win_point = 0
        constant_loss_time = 0
        constant_loss_point = 0
        for profit in df_datas['profit']:
            if profit >0:
                constant_win_time += 1
                max_constant_win_time = max(max_constant_win_time, constant_win_time)
                constant_loss_time = 0

                constant_win_point += profit
                max_constant_win_point = max(max_constant_win_point, constant_win_point)
                constant_loss_point = 0
            elif profit <0:
                constant_loss_time += 1
                max_constant_loss_time = max(max_constant_loss_time, constant_loss_time)
                constant_win_time = 0

                constant_loss_point += profit
                max_constant_loss_point = min(max_constant_loss_point, constant_loss_point)
                constant_win_point = 0
            else:
                constant_win_time = 0
                constant_win_point = 0
                constant_loss_time = 0
                constant_loss_point = 0
            total_profit += profit
            max_total_profit = max(max_total_profit, total_profit)
            retrace = 0
            if max_total_profit !=0:retrace = (max_total_profit - total_profit)/float(abs(max_total_profit))
            max_retrace = max(max_retrace, retrace)

        log.WriteLog(LOG_SUMMARY_REPORT, u"盈利点数:%d"%total_profit)
        log.WriteLog(LOG_SUMMARY_REPORT, u"开仓次数:%d"%open_time)
        log.WriteLog(LOG_SUMMARY_REPORT, u"盈利次数:%d  盈利点数%.2f"%(win_time,win_point))
        log.WriteLog(LOG_SUMMARY_REPORT, u"亏损次数:%d  亏损点数%.2f"%(loss_time,loss_point))
        log.WriteLog(LOG_SUMMARY_REPORT, u"胜率:%.2f  盈亏比%.2f"%(win_ratio,win_loss_ratio))
        log.WriteLog(LOG_SUMMARY_REPORT, u"单笔最大收益点数:%.2f  单笔最大亏损点数%.2f"%(max_win_point,max_loss_point))
        log.WriteLog(LOG_SUMMARY_REPORT, u"最大连胜次数:%d  最大连胜点数%.2f"%(max_constant_win_time,max_constant_win_point))
        log.WriteLog(LOG_SUMMARY_REPORT, u"最大连亏次数:%.2f  最大连亏点数%.2f"%(max_constant_loss_time,max_constant_loss_point))
        log.WriteLog(LOG_SUMMARY_REPORT, u"最大回撤:%.2f%%"%(max_retrace*100))
        if not is_testCase: return 
        if total_profit != 102 or open_time !=3 or win_time !=2 or win_point != 152 or loss_time != 1 or loss_point != -50 \
            or round(win_ratio,2) !=0.67 or win_loss_ratio !=1.52 or max_win_point != 126 or max_loss_point !=-50 \
            or max_constant_win_time != 2 or max_constant_win_point != 152 or max_constant_loss_time != 1 or max_constant_loss_point !=-50\
            or max_retrace !=0:
            raise ValueError('error function add_up')

    def record_position_situation(this):
        pass

    def add_record(this, datestamp, dict):
        log.WriteLog('add_record', '%s  %s'%(str(datestamp), dict))
        if dict is None : return
        for key in dict.keys():
            if key not in this.df_records.columns:
                raise 'add_record error: key error'
        if not dict.has_key('id'):raise 'add_record error: has no key:id'

        row =pd.DataFrame(dict,index =[datestamp])
        this.df_records = this.df_records.append(row)

    def get_open_times(this, id = None): #获取开仓次数
        df_index = this.df_records['profit'].isnull()
        if id is not None:
            df_index = df_index & (this.df_records['id'] == id)
        df = this.df_records[df_index]
        return len(df)

    def get_win_situation(this, id = None): #返回盈利次数、盈利点数
        df_index = this.df_records['profit']>0
        if id is not None:
            df_index = df_index & (this.df_records['id'] == id)
        df = this.df_records[df_index]
        return len(df), df['profit'].sum()

    def get_loss_situation(this, id = None):  #返回亏损次数、亏损点数
        df_index = this.df_records['profit']<0
        if id is not None:
            df_index = df_index & (this.df_records['id'] == id)
        df = this.df_records[df_index]
        return len(df), df['profit'].sum()

    def get_max_win_point(this, id = None):  #单笔最大盈利点数
        df_index = this.df_records['profit']>0
        if id is not None:
            df_index = df_index & (this.df_records['id'] == id)
        df = this.df_records[df_index]
        return df['profit'].max()

    def get_max_loss_point(this, id = None):  #单笔最大亏损点数
        df_index = this.df_records['profit']<0
        if id is not None:
            df_index = df_index & (this.df_records['id'] == id)
        df = this.df_records[df_index]
        return df['profit'].min()

    def get_records(this):
        return this.df_records

    def get_records_by_id(this, id):
        return this.df_records[this.df_records['id'] == id]

    def write_record_to_csv(this):
        this.df_records.to_csv('record.csv')