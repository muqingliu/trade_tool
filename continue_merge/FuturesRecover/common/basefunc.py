# -*- coding: utf-8 -*-
# @Time    : 2017/4/20 10:53
# @Author  : hc
# @Site    :
# @File    : basefunc.py
# @Software: PyCharm

# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

import db
import pyetc as py_etc
from define import sys_conf_define


def get_config_DB():

    config = py_etc.load(sys_conf_define.BASE_PATH + r'\define\db_define.py')

    return config.DB


def get_config_sys():
    config = py_etc.load(r'define\sys_conf_define.py')
    return config


def create_database(info=None):
    if info is None:
        info = get_config_DB()
    print("connect to host[%s] user[%s] db[%s] port[%s]" %
          (info['HOST'], info['USER'], info['DB'], info['PORT']))
    return db.DB(
        host=info['HOST'],
        user=info['USER'],
        pass_wd=info['PASSWORD'],
        db=info['DB'],
        charset=info['CHARSET'],
        port=info['PORT'])


if __name__ == '__main__':
    print sys.version
    print(get_config_DB())
    db = create_database()
    q = "select * from hq_cffex_k1 limit 1"
    db.Query(q)
    res = db.FetchAll()
    print(res)
