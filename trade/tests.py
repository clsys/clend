from django.test import TestCase

# Create your tests here.
from datafeed import get_datafeed
from constant import Interval, Exchange
from object import HistoryRequest
from datetime import datetime
from hs_udata import stock_list, set_token, stock_quote_minutes
def main1():
    datafeed = get_datafeed()
    # symbol: str=''
    # exchange: Exchange=Exchange.CFFEX
    # start: datetime=
    # end: datetime = None
    # interval: Interval = Interval.MINUTE
    req = HistoryRequest(
        symbol='IF2110',
        exchange=Exchange.CFFEX,
        interval=Interval.MINUTE,
        start=datetime(2021, 8, 10),
        end=datetime(2021, 9, 10)
    )
    bars = datafeed.query_bar_history(req)
    print(bars)


if __name__ == '__main__':
    set_token(token='r_atbJBC_zlpqbzepTwi4c0s4F0dkJ0KHtdQnMgJDK0bQRAX8t8P0YlNj3si_f4s')
    s=stock_list()
    print(s)
    # bar = stock_quote_minutes("600519.SH", "2021-8-9", "2021-10-1")
    # print(bar)
