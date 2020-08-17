
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import unittest 
import test_case
from report_manager import *

class TestCase_report_mgr(unittest.TestCase):
    def setUp(this):
        this.report_mgr = class_report_mgr()
        this.report_mgr.add_record(pd.to_datetime('2010/02/01-14:00'),{'number': 1, 'id': 'TA01-05_diff.data', 'dir': 1, 'point': -286})
        this.report_mgr.add_record(pd.to_datetime('2011/01/24-10:00'),{'number': 1, 'id': 'TA01-05_diff.data', 'dir': 0, 'profit': -50})
        this.report_mgr.add_record(pd.to_datetime('2012/01/31-15:00'),{'number': 1, 'id': 'TA01-05_diff.data', 'dir': 1, 'point': 84})
        this.report_mgr.add_record(pd.to_datetime('2012/02/01-11:30'),{'number': 1, 'id': 'TA01-05_diff.data', 'dir': 0, 'profit': 26})
        this.report_mgr.add_record(pd.to_datetime('2013/01/22-09:30'),{'number': 1, 'id': 'TA01-05_diff.data', 'dir': 0, 'point': 186})
        this.report_mgr.add_record(pd.to_datetime('2014/01/21-11:00'),{'number': 1, 'id': 'TA01-05_diff.data', 'dir': 1, 'profit': 126})


    def tearDown(this):
        this.report_mgr = None


    def test_add_up(this):
        this.report_mgr.add_up('TA01-05_diff.data',True)
        
    def test_get_open_times(this):
        cmp_times = 3
        open_times = this.report_mgr.get_open_times('TA01-05_diff.data')
        this.assertEqual(cmp_times, open_times)

    def test_get_win_situation(this):
        cmp_times = 2
        cmp_points = 152
        win_times,win_points = this.report_mgr.get_win_situation('TA01-05_diff.data')
        this.assertEqual(cmp_times, win_times)
        this.assertEqual(cmp_points, win_points)

    def test_get_loss_situation(this):
        cmp_times = 1
        cmp_points = -50
        loss_times,loss_points = this.report_mgr.get_loss_situation('TA01-05_diff.data')
        this.assertEqual(cmp_times, loss_times)
        this.assertEqual(cmp_points, loss_points)

    def test_get_max_win_point(this):
        cmp_point = 126
        max_win_point = this.report_mgr.get_max_win_point('TA01-05_diff.data')
        this.assertEqual(cmp_point, max_win_point)

    def test_get_max_loss_point(this):
        cmp_point = -50
        max_loss_point = this.report_mgr.get_max_loss_point('TA01-05_diff.data')
        this.assertEqual(cmp_point, max_loss_point)


if __name__ == '__main__':
    suite = unittest.TestSuite() 
    suite.addTest(TestCase_report_mgr("test_add_up"))
    suite.addTest(TestCase_report_mgr("test_get_open_times"))
    suite.addTest(TestCase_report_mgr("test_get_win_situation"))
    suite.addTest(TestCase_report_mgr("test_get_loss_situation"))
    suite.addTest(TestCase_report_mgr("test_get_max_win_point"))
    suite.addTest(TestCase_report_mgr("test_get_max_loss_point"))
    runner = unittest.TextTestRunner()
    runner.run(suite) 