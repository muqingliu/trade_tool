
import data_manager
import plot_manager
import report_manager
import position_mgr
import numpy as np
import pandas as pd
import log

class policy_class_select_base(object):
    def init(this, data_mgr, position_mgr, select_id):
        this.data_mgr = data_mgr
        this.position_mgr = position_mgr
        this.select_id = select_id
        pass

    def process(this, datestamp, all_positions):
        pass

class policy_class_trade_base(object):
    def init(this, data_mgr, position_mgr, report_mgr):
        this.data_mgr = data_mgr
        this.position_mgr = position_mgr
        this.report_mgr = report_mgr
        pass

    def open(this, datestamp, id, number, dir = 1): #dir=1 买多 dir = 0 卖空
        point = this.data_mgr.get_point(id, datestamp)
        if point is None: return
        this.position_mgr.add_position(datestamp, id, point, number, dir)
        this.report_mgr.add_record(datestamp,{'id':id, 'point':point,'number':number,'dir':1})
        pass

    def close(this, datestamp, id, number):
        point = this.data_mgr.get_point(id, datestamp)
        if point is None: return
        dir = this.position_mgr.get_position_dir_by_id(id)
        if dir is None: return 
        remove_point, remove_num = this.position_mgr.remove_position(id, number)
        profit_point = (point - remove_point)*remove_num
        if dir ==0:profit_point = -profit_point
        this.report_mgr.add_record(datestamp,{'id':id, 'point':point,'number':number,'dir':0, 'profit':profit_point})


    def process(this, datestamp, buy_ids, sell_ids):
        pass


class class_policy_select(policy_class_select_base):
    def __init__(this):
        this.buy_param = 0.75 #买入参数


    def init(this, data_mgr, position_mgr, select_id):
        policy_class_select_base.init(this, data_mgr, position_mgr, select_id)
        this.mu = this.data_mgr.get_mu()
        this.sigma = this.data_mgr.get_sigma()
        this.up_boundary = this.mu + 2*this.sigma
        this.down_boundary = this.mu - 2*this.sigma

    def process(this, datestamp, next_datestamp, all_positions):
        this.up_buy = this.mu + this.buy_param*this.sigma
        this.down_buy = this.mu - this.buy_param*this.sigma

        belong_slice_time = this.data_mgr.get_belong_slice_time(this.select_id, datestamp)
        if belong_slice_time is None: return None,None

        point = this.data_mgr.get_point(this.select_id, datestamp)
        if datestamp == belong_slice_time[0] and (point >= this.up_boundary or point <= this.down_boundary):
            this.up_boundary = point + 1.25*this.sigma
            this.down_boundary = point - 1.25*this.sigma
            return [(this.select_id,0)],[]

        if next_datestamp is None or belong_slice_time != this.data_mgr.get_belong_slice_time(this.select_id, next_datestamp): 
            this.buy_param = 0.75 
            this.up_boundary = this.mu + 2*this.sigma
            this.down_boundary = this.mu - 2*this.sigma
            if all_positions.has_key(this.select_id):#需换期
                open_datestamp = all_positions[this.select_id].datetime
                this.position_mgr.wait_change_period(this.select_id, open_datestamp)
                log.WriteLog('wait_change_period', '%s\t%s'%(this.select_id, str(open_datestamp)))         
                return [], [this.select_id]  #当期结束时卖出

        
        if all_positions.has_key(this.select_id):
            if point >= this.up_boundary or point <=this.down_boundary:  #止损卖出
                this.buy_param = 0.8
                this.up_boundary = this.mu + 2*this.sigma
                this.down_boundary = this.mu - 2*this.sigma
                return [], [this.select_id]

            position_point = this.position_mgr.get_position_price_by_id(this.select_id)
            if (position_point < this.mu and point >= this.mu) or (position_point>this.mu and point <= this.mu): #盈利卖出
                this.up_boundary = this.mu + 2*this.sigma
                this.down_boundary = this.mu - 2*this.sigma
                this.buy_param = 0.75
                return [], [this.select_id]            
        else:
            if not this.data_mgr.is_delivery_day(this.select_id, datestamp):
                if (this.buy_param ==0.75 and (point >= this.up_buy and point < this.up_boundary)) or (this.buy_param ==0.8 and point <= this.up_buy and point > this.mu):
                    return [(this.select_id,0)],[]
                elif (this.buy_param ==0.75 and (point <= this.down_buy and point >this.down_boundary)) or (this.buy_param ==0.8 and point >= this.down_buy and point < this.mu):
                    return [(this.select_id,1)],[]
                  
        return None, None

class class_policy_trade(policy_class_trade_base):
    def process(this, datestamp, open_ids, close_ids):
        if open_ids is None and close_ids is None: return 
        for id,dir in open_ids:
            this.open(datestamp, id, 1,dir)
        for id in close_ids:
            this.close(datestamp,id,1)
        pass




class class_trader_sys(object):
    def __init__(this, data_dir_path, time_slice_cfg_path, policy_select, policy_trade, select_id):
        this.select_id = select_id
        this.data_mgr = data_manager.class_data_manager(data_dir_path, time_slice_cfg_path)
        this.plot_mgr = plot_manager.class_plot_manager()
        this.position_mgr = position_mgr.class_position_mgr()
        this.report_mgr = report_manager.class_report_mgr()
        this.policy_select = policy_select
        this.policy_select.init(this.data_mgr, this.position_mgr, select_id)
        this.policy_trade = policy_trade
        this.policy_trade.init(this.data_mgr, this.position_mgr, this.report_mgr)
        pass

    def plot(this):
        df_datas = this.data_mgr.get_all_datas()
        mu = this.data_mgr.get_mu()
        sigma = this.data_mgr.get_sigma()
        #绘制直方图
        #this.plot_mgr.plot_normal_distribution(df_datas, mu, sigma)

        ##中值、上买入线、上止损线、下买入线、下止损先
        up_boundary = mu + 2*sigma
        down_boundary = mu - 2*sigma
        up_buy = mu + 0.75*sigma
        down_buy = mu - 0.75*sigma

        for file_name in this.data_mgr.get_data_file_names():
            slice_times = this.data_mgr.get_file_slice_times(file_name)
            file_datas = this.data_mgr.get_file_datas(file_name)
            this.plot_mgr.plot_sectional_curve(file_name, file_datas, slice_times, [up_boundary, up_buy, mu, down_buy, down_boundary, mu + 0.8*sigma, mu - 0.8*sigma])
            break
        this.plot_mgr.show()

        file_obj = open('info.log','w')
        file_obj.write("mu:%.2f  sigma:%.2f up_boundary:%.2f  down_boundary:%.2f  up_buy:%.2f  down_buy:%.2f"%(mu,sigma,up_boundary,down_boundary,up_buy,down_buy))
        file_obj.close()


    def process(this):
        #this.plot()
        dates = this.data_mgr.get_trade_datestamps_by_id(this.select_id)

        mu = this.data_mgr.get_mu()
        sigma = this.data_mgr.get_sigma()
        ##中值、上买入线、上止损线、下买入线、下止损先
        up_boundary = mu + 2*sigma
        down_boundary = mu - 2*sigma
        up_buy = mu + 0.75*sigma
        down_buy = mu - 0.75*sigma

        index = 0
        for datestamp in dates:
            all_positions = this.position_mgr.get_all_positions()
            next_datestamp = None
            if index != len(dates) - 1: next_datestamp = dates[index + 1]
            buy_ids, sell_ids = this.policy_select.process(datestamp, next_datestamp, all_positions)
            this.policy_trade.process(datestamp, buy_ids, sell_ids)
            index += 1 
            if index == len(dates):
                for id in all_positions.keys():
                    datestamp = all_positions[id].datetime
                    this.position_mgr.wait_change_period(id, datestamp)
                    log.WriteLog('wait_change_period', '%s\t%s'%(id, str(datestamp)))  

                this.report_mgr.write_record_to_csv()
                this.report_mgr.add_up(this.select_id)
                this.plot_mgr.plot_bar(this.report_mgr.get_records())
                this.plot_mgr.plot_cumsum_profit_curve(this.report_mgr.get_records())

                wait_change_period = this.position_mgr.get_wait_change_period(this.select_id)
                this.plot_mgr.plot_trade_point(this.report_mgr.get_records(), wait_change_period, [up_boundary, up_buy, mu, down_buy, down_boundary])
                this.plot_mgr.show()
        



if __name__ == '__main__':
    policy_select = class_policy_select()
    policy_trade = class_policy_trade()

    trader_sys = class_trader_sys(r'testCase\testData',r'testCase\testData\time_slice.cfg', policy_select, policy_trade, select_id = 'TA01_05_same.log')
    trader_sys.process()