# -*- coding: utf-8 -*-
import asyncio
import json
import warnings
import re
import aiohttp
import easyutils
import yarl
from common import log
from . import helpers
from common import pyetc

class BaseQuotation:
    """行情获取基类"""
    max_num = 300  # 每次请求的最大股票数
    stock_api = ''  # 股票 api

    def __init__(self):
        self._session = None
        stock_codes = self.load_stock_codes()
        self.stock_list = self.gen_stock_list(stock_codes)

    @staticmethod
    def filter_stock_codes(stock_with_exchange_list,type="A"):
        res=[]
        if type == "A":
            for stock in stock_with_exchange_list:
                if re.findall(r'sh60\d*', stock) or re.findall(r'sz002\d*', stock) or re.findall(r'sz300\d*',stock) or re.findall(r'sz000\d*', stock):
                    res.append(stock)
            return res

    def gen_stock_list(self, stock_codes):
        stock_codes =[stock[0] for stock in stock_codes]
        stock_codes.sort()
        print("stock_codes 数量为：",len(stock_codes))
        if len(stock_codes) < self.max_num:
            request_list = ','.join(stock_codes)
            return [request_list]

        stock_list = []
        request_num = len(stock_codes) // self.max_num + 1
        for range_start in range(request_num):
            num_start = self.max_num * range_start
            num_end = self.max_num * (range_start + 1)
            request_list = ','.join(stock_codes[num_start:num_end])
            stock_list.append(request_list)
        return stock_list

    @staticmethod
    def load_stock_codes(real_time= False ,stock_type="stock",with_exchange=True):
        return helpers.get_stock_codes(real_time=real_time,stock_type=stock_type,with_exchange=with_exchange)

    @property
    def all(self):
        warnings.warn('use all_market instead', DeprecationWarning)
        return self.get_stock_data(self.stock_list)

    @property
    def all_market(self):
        """return quotation with stock_code prefix key"""
        return self.get_stock_data(self.stock_list, prefix=True)

    def stocks(self, stock_codes):
        if type(stock_codes) is not list:
            stock_codes = [stock_codes]

        stock_list = self.gen_stock_list(stock_codes)
        return self.get_stock_data(stock_list)

    def fetch_stocks(self, stock_codes):
        if type(stock_codes) is not list:
            stock_codes = [stock_codes]

        stock_list = self.gen_stock_list(stock_codes)
        return self.get_stock_data(stock_list, prefix=True)

    async def get_stocks_by_range(self, params):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
        }
        url = yarl.URL(self.stock_api % (params), encoded=True)
        print(self.stock_api % (params))
        try:
            async with self._session.get(url, timeout=20, headers=headers) as r:
                response_text = await r.text()
                return response_text
        except asyncio.TimeoutError:
            return None

    def get_stock_data(self, stock_list, **kwargs):
        coroutines = []

        for params in stock_list:
            coroutine = self.get_stocks_by_range(params)
            coroutines.append(coroutine)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        res = loop.run_until_complete(asyncio.gather(*coroutines))

        return self.format_response_data([x for x in res if x is not None], **kwargs)

    def __del__(self):
        if self._session is not None:
            self._session.close()

    def format_response_data(self, rep_data, **kwargs):
        pass
