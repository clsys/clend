# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 17:24:55 2021

@author: leida
"""

import requests
import random
import requests, json
import sys
import pandas as pd
from io import StringIO
import multiprocessing
import numpy
from clend.settings import SETTINGS
from trade.object import BarData, HistoryRequest
from hs_udata.apis.stock.api import stock_quote_minutes
from trade.feed.udata.udata_datafeed import UdataDatafeed, Interval, Exchange
from datetime import timedelta, datetime


class Data:
    token = None

    # symbol股票编号，scale数据的时间间隔，ma均值，datalen数据长度（最大1023）
    def __init__(self):
        self._data = UdataDatafeed()

    def get_data(self, response):  # 数据处理函数,处理csv字符串函数
        '''格式化数据为DataFrame'''
        return pd.read_csv(StringIO(response.text)).values.tolist()

    def get_bars(self, symbol, datalen, day, unit):
        end = datetime.strptime(day, '%Y-%m-%d')
        start = end - timedelta(days=datalen)
        print(str(start)+":"+str(end)+";"+symbol.split('.', 1)[0])
        return self._data.query_stock_bars(HistoryRequest(
            symbol=symbol,
            exchange=Exchange.SZSE,
            interval=Interval.MINUTE,
            start=start,
            end=end
        ))

    def get_all_securities(self, date=None):
        return self._data.query_all_securities(None)
