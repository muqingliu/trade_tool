
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import unittest 
import test_case
from  data_manager  import *

class TestCase_data_manager(unittest.TestCase):
    def setUp(this):
        this.data_mgr = class_data_manager(r'testCase\testData',r'testCase\testData\time_slice.cfg')

    def tearDown(this):  
        this.data_mgr = None

    def test_get_all_datas(this):
        all_datas = this.data_mgr.get_all_datas()
        this.assertEqual(np.array_equal(test_case.test_datas_1,all_datas), True)
        

    def test_get_file_datas(this):
        file_datas = this.data_mgr.get_file_datas('TA01-05_same.data')
        this.assertEqual(np.array_equal(test_case.test_datas_2,file_datas), True)

    def test_get_data_file_names(this):
        cmp_file_names = ['TA01-05_same.data', 'TA01-05_diff.data']
        file_names = this.data_mgr.get_data_file_names()
        this.assertEqual(cmp(cmp_file_names, file_names), 0) 

    def test_get_file_slice_times(this):
        slice_times = this.data_mgr.get_file_slice_times('TA01-05_same.data')
        this.assertEqual(np.array_equal(test_case.test_datas_3,slice_times), True) 

    def test_get_file_slice_datas(this):
        file_slice_datas = this.data_mgr.get_file_slice_datas('TA01-05_same.data',"2010/05/31-09:30","2012/05/17-10:00")
        this.assertEqual(np.array_equal(test_case.test_datas_4,file_slice_datas), True)

    #def test_get_file_all_slice_datas(this):
    #    all_slice_datas = this.data_mgr.get_file_all_slice_datas('TA01-05_same.data')
    #    this.assertEqual(np.array_equal(test_case.test_datas_5,all_slice_datas), True)

if __name__ == '__main__':
     suite = unittest.TestSuite()  
     suite.addTest(TestCase_data_manager("test_get_all_datas")) 
     suite.addTest(TestCase_data_manager("test_get_file_datas")) 
     suite.addTest(TestCase_data_manager("test_get_data_file_names")) 
     suite.addTest(TestCase_data_manager("test_get_file_slice_times")) 
     suite.addTest(TestCase_data_manager("test_get_file_slice_datas")) 
     runner = unittest.TextTestRunner() 
     runner.run(suite)