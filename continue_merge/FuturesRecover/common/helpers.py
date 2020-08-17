# coding:utf8
import json
import os
import re
import sys

import requests
import easyutils

STOCK_CODE_PATH = 'stock_codes.conf'

def gen_stock_header(stock):
    """在股票ID前面增加对应的证券市场简称
    """
    stock = str(stock)
    return easyutils.stock.get_stock_type(stock) + stock[-6:]

def update_stock_codes():
    """获取所有股票 ID 及 名称 到 STOCK_CODE_PATH 文件中
    """
    all_stock_codes_url = 'http://www.shdjt.com/js/lib/astock.js'
    grep_stock_codes = re.compile('~(\d+)`')
    response = requests.get(all_stock_codes_url)
    all_stock_codes = grep_stock_codes.findall(response.text)
    with open(stock_code_path(), 'w') as f:
        f.write(json.dumps(dict(stock=all_stock_codes)))


def get_stock_codes(real_time = False,stock_type = None,with_exchange = False):
    """获取所有股票 ID 到 all_stock_code 目录下
    real_time:是否实时
    stock_type:(fund 基金 stock 股票)
    with_exchange:是否要加上对应的证券市场编码
    """
    if real_time:
        all_stock_codes_url = 'http://www.shdjt.com/js/lib/astock.js'
        grep_stock_format = '~(\w+)`([^`]+)`'
        grep_stock_codes = re.compile(grep_stock_format)
        response = requests.get(all_stock_codes_url)
        # 这里对id去重
        stock_codes = list(set(grep_stock_codes.findall(response.text)))
        with open(stock_code_path(), 'w') as f:
            f.write(json.dumps(dict(stock=stock_codes),ensure_ascii=False))
    else:
        with open(stock_code_path()) as f:
            stock_codes= json.load(f)['stock']

    if stock_type:
        stock_codes =[(stock[0],stock[1]) for stock in stock_codes if stock_type == str(easyutils.stock.get_code_type(stock[0])) ]

    if with_exchange:
        stock_codes = [(gen_stock_header(code[0]), code[1]) for code in stock_codes]
    return stock_codes

def stock_code_path():
    if getattr(sys,'frozen',False):
        pathname = STOCK_CODE_PATH
    else:
        pathname = os.path.join(os.path.dirname(__file__), STOCK_CODE_PATH)
    return pathname
