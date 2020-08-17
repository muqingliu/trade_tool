
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import unittest 
import test_case
from position_mgr import *

class TestCase_position_mgr(unittest.TestCase):
    def setUp(this):
        this.position_mgr = class_position_mgr()
        this.position_mgr.add_position(pd.to_datetime('2010/05/31-09:30'),'TA01-05_same.data',-184,2,1)
        this.position_mgr.add_position(pd.to_datetime('2013/01/18-11:30'),'TA01-05_diff.data',262,2,0)
        pass

    def tearDown(this): 
        this.position_mgr = None 
        pass


    def compare_all_positions(this, cmp_datas, function_name):
        position_datas = this.position_mgr.get_all_positions()
        for id, positions in position_datas.iteritems():
            if not cmp_datas.has_key(id): 
                raise ValueError('error function %s'%function_name)
            cmp_position = cmp_datas[id]
            if cmp_position.datetime != positions.datetime or cmp_position.price != positions.price or cmp_position.number != positions.number or cmp_position.dir != positions.dir:
                raise ValueError('error function %s'%function_name)


    def test_add_position(this):
        cmp_datas = {'TA01-05_same.data':class_position(pd.to_datetime('2010/05/31-09:30'), -184, 2, 1),'TA01-05_diff.data':class_position(pd.to_datetime('2013/01/18-11:30'), 262, 2, 0)}
        this.compare_all_positions(cmp_datas, 'test_add_position')


    def test_remove_position(this):
        this.position_mgr.remove_position('TA01-05_same.data',1)
        cmp_datas = {'TA01-05_same.data':class_position(pd.to_datetime('2010/05/31-09:30'), -184, 1, 1),'TA01-05_diff.data':class_position(pd.to_datetime('2013/01/18-11:30'), 262, 2, 0)}
        this.compare_all_positions(cmp_datas, 'test_remove_position')


    def test_wait_change_period(this):
        this.position_mgr.wait_change_period('TA01-05_same.data',pd.to_datetime('2010/05/31-09:30'))
        if cmp(this.position_mgr.wait_change_period_ids.keys(),['TA01-05_same.data']) !=0 \
            or this.position_mgr.wait_change_period_ids['TA01-05_same.data'] != [pd.to_datetime('2010/05/31-09:30')]:
            raise ValueError('error function test_wait_change_period')


    def test_get_position_by_id(this):
        cmp_position = class_position(pd.to_datetime('2010/05/31-09:30'), -184, 2, 1)
        positions = this.position_mgr.get_position_by_id('TA01-05_same.data')
        if positions is None: raise ValueError('error function test_get_position_by_id')
        if cmp_position.datetime != positions.datetime or cmp_position.price != positions.price or cmp_position.number != positions.number or cmp_position.dir != positions.dir:
            raise ValueError('error function test_get_position_by_id')

    def test_get_all_positions(this):
        cmp_datas = {'TA01-05_same.data':class_position(pd.to_datetime('2010/05/31-09:30'), -184, 2, 1),'TA01-05_diff.data':class_position(pd.to_datetime('2013/01/18-11:30'), 262, 2, 0)}
        this.compare_all_positions(cmp_datas, 'test_get_all_positions')

    def test_get_position_ids(this):
        cmp_ids = ['TA01-05_same.data', 'TA01-05_diff.data']
        ids = this.position_mgr.get_position_ids()
        this.assertEqual(cmp(cmp_ids, ids), 0)
        
        
    def test_get_position_number_by_id(this):
        cmp_num = 2
        num = this.position_mgr.get_position_number_by_id('TA01-05_same.data')
        this.assertEqual(cmp_num, num)


    def test_get_position_price_by_id(this):
        cmp_price = -184
        price = this.position_mgr.get_position_price_by_id('TA01-05_same.data')
        this.assertEqual(cmp_price, price)






if __name__ == '__main__':
    suite = unittest.TestSuite() 
    #suite.addTest(TestCase_position_mgr("test_add_position")) 
    #suite.addTest(TestCase_position_mgr("test_remove_position")) 
    suite.addTest(TestCase_position_mgr("test_wait_change_period")) 
    suite.addTest(TestCase_position_mgr("test_get_position_by_id")) 
    suite.addTest(TestCase_position_mgr("test_get_all_positions"))
    suite.addTest(TestCase_position_mgr("test_get_position_ids"))
    suite.addTest(TestCase_position_mgr("test_get_position_number_by_id"))
    suite.addTest(TestCase_position_mgr("test_get_position_price_by_id"))
    runner = unittest.TextTestRunner()
    runner.run(suite) 