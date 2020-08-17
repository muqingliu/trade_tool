import pandas as pd
import unittest
from TestCase_data_manager import *
from TestCase_plot_manager  import *
from TestCase_position_mgr import *
from TestCase_report_mgr import *

dates_1 = ['2010/05/31-09:30','2010/05/31-10:00','2011/05/17-09:30','2011/05/17-10:00','2012/05/17-09:30','2012/05/17-10:00','2013/05/17-09:30','2013/05/17-10:00','2014/05/19-09:30','2014/05/19-10:00','2015/05/18-09:30','2015/05/18-10:00','2010/02/01-09:30','2010/02/01-14:00','2011/01/24-09:30','2011/01/24-10:00','2012/01/31-15:00','2012/02/01-11:30','2013/01/18-11:30','2013/01/22-09:30','2014/01/17-14:00','2014/01/21-11:00','2015/01/19-09:30','2015/01/19-11:30']
values_1 = [-184,-188,-124,-144,-166,-2,16,26,-20,-46,-54,-44,-402,-286,-268,-336,84,110,262,186,66,60,-130,-134]
test_datas_1 = pd.DataFrame(values_1, index=pd.to_datetime(dates_1))


dates_2 =['2010/05/31-09:30','2010/05/31-10:00', '2011/05/17-09:30', '2011/05/17-10:00', '2012/05/17-09:30', '2012/05/17-10:00', '2013/05/17-09:30','2013/05/17-10:00','2014/05/19-09:30','2014/05/19-10:00','2015/05/18-09:30','2015/05/18-10:00']
values_2 = [-184,-188,-124,-144,-166,-2,16,26,-20,-46,-54,-44]
test_datas_2 = pd.DataFrame(values_2, index=pd.to_datetime(dates_2))

test_datas_3 = []
test_slice_times = [("2010/05/31-09:30","2010/05/31-10:00"),("2011/05/17-09:30","2011/05/17-10:00"),("2012/05/17-09:30","2012/05/17-10:00"),("2013/05/17-09:30","2013/05/17-10:00"),("2014/05/19-09:30","2014/05/19-10:00"),("2015/05/18-09:30","2015/05/18-10:00")]
for slice_time in test_slice_times:
    beg_date = pd.to_datetime(slice_time[0])
    end_date = pd.to_datetime(slice_time[1])
    test_datas_3.append((beg_date, end_date))

dates_4 = ['2010/05/31-09:30','2010/05/31-10:00','2011/05/17-09:30','2011/05/17-10:00','2012/05/17-09:30','2012/05/17-10:00']
values_4 = [-184,-188,-124,-144,-166,-2]
test_datas_4 = pd.DataFrame(values_4, index=pd.to_datetime(dates_4))

dates_5 = ['2010/05/31-09:30','2010/05/31-10:00','2011/05/17-09:30','2011/05/17-10:00','2012/05/17-09:30','2012/05/17-10:00','2013/05/17-09:30','2013/05/17-10:00','2014/05/19-09:30','2014/05/19-10:00','2015/05/18-09:30','2015/05/18-10:00']
values_5 = [-184,-188,-124,-144,-166,-2,16,26,-20,-46,-54,-44]
test_datas_5 = pd.DataFrame(values_5, index=pd.to_datetime(dates_5))



if __name__ == '__main__':
    suite = unittest.TestSuite()  
    suite.addTest(TestCase_data_manager("test_get_all_datas")) 
    suite.addTest(TestCase_data_manager("test_get_file_datas")) 
    suite.addTest(TestCase_data_manager("test_get_data_file_names")) 
    suite.addTest(TestCase_data_manager("test_get_file_slice_times")) 
    suite.addTest(TestCase_data_manager("test_get_file_slice_datas")) 

    runner = unittest.TextTestRunner() 
    runner.run(suite)  