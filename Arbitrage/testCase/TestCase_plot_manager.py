
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import unittest 
import test_case
from plot_manager import *

class TestCase_plot_manager(unittest.TestCase):
    def setUp(this):
        this.plot_mgr = class_plot_manager()

    def tearDown(this): 
        this.plot_mgr = None

    def test_get_color(this):
        this.plot_mgr.get_color()

    def test_create_figure(this):
        this.plot_mgr.create_figure()

    def test_plot_normal_distribution(this):#测试直方图是否正确
        test_datas = pd.DataFrame(test_case.values_1, index=pd.to_datetime(test_case.dates_1), columns=['point'])
        this.plot_mgr.plot_normal_distribution(test_datas, None, None, True)

    def test_plot_parallel_lines(this):
        this.plot_mgr.plot_parallel_lines([3,6,10], 50)

    def test_plot_single_slice_line(this):
        df_datas = pd.DataFrame(test_case.values_1, index=pd.to_datetime(test_case.dates_1), columns=['point'])
        slice_time = (pd.to_datetime('2010/05/31-10:00'),pd.to_datetime('2015/01/19-09:30'))
        this.plot_mgr.plot_single_slice_line('TA01-05_same.data',df_datas, slice_time)

    def test_plot_sectional_curve(this):
        df_datas = pd.DataFrame(test_case.values_1, index=pd.to_datetime(test_case.dates_1), columns=['point'])
        dates = [('2010/05/31-09:30','2012/05/17-09:30'),('2012/05/17-10:00','2015/05/18-09:30'),('2015/05/18-10:00','2015/01/19-11:30')]
        slice_times = []
        for date in dates:
            slice_time = (pd.to_datetime(date[0]), pd.to_datetime(date[1]))
            slice_times.append(slice_time)
        this.plot_mgr.plot_sectional_curve('TA01-05_same.data',df_datas, slice_times)

    def test_plot_bar(this):
        df_datas = pd.DataFrame(test_case.values_1, index=pd.to_datetime(test_case.dates_1), columns=['profit'])
        this.plot_mgr.plot_bar(df_datas)
        

    def test_set_xticks(this):
        this.plot_mgr.set_xticks(pd.to_datetime(test_case.dates_1))

    def test_plot_cumsum_profit_curve(this):
        df_records = pd.DataFrame(test_case.values_1, index=pd.to_datetime(test_case.dates_1), columns=['profit'])
        this.plot_mgr.plot_cumsum_profit_curve(df_records)

    def test_plot_trade_point(this):
        df_records = pd.DataFrame({'number':[1,1,1,1,1,1],
                                   'id':['TA01-05_diff.data', 'TA01-05_diff.data', 'TA01-05_diff.data', 'TA01-05_diff.data', 'TA01-05_diff.data', 'TA01-05_diff.data'],
                                   'dir':[1,0,1,0,0,1],
                                   'point':[-286, np.nan, 84, np.nan, 186,np.nan],
                                   'profit':[np.nan, -50, np.nan, 26, np.nan, 126]},index = pd.to_datetime(['2010/02/01-14:00','2011/01/24-10:00','2012/01/31-15:00','2012/02/01-11:30', '2013/01/22-09:30','2014/01/21-11:00']))


        this.plot_mgr.plot_trade_point(df_records, [pd.to_datetime('2012/01/31-15:00')])


if __name__ == '__main__':
    suite = unittest.TestSuite()  
    suite.addTest(TestCase_plot_manager("test_get_color")) 
    suite.addTest(TestCase_plot_manager("test_create_figure")) 
    suite.addTest(TestCase_plot_manager("test_plot_normal_distribution")) 
    suite.addTest(TestCase_plot_manager("test_plot_parallel_lines")) 
    suite.addTest(TestCase_plot_manager("test_plot_single_slice_line"))
    suite.addTest(TestCase_plot_manager("test_plot_sectional_curve"))
    suite.addTest(TestCase_plot_manager("test_plot_bar"))  
    suite.addTest(TestCase_plot_manager("test_set_xticks"))
    suite.addTest(TestCase_plot_manager("test_plot_cumsum_profit_curve")) 
    suite.addTest(TestCase_plot_manager("test_plot_trade_point"))     
    runner = unittest.TextTestRunner() 
    runner.run(suite) 