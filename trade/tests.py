from django.test import TestCase

# Create your tests here.
from datafeed import get_datafeed
from constant import Interval
from object import HistoryRequest
from datetime import datetime
from chanlun.strategies.mychan import JChan
import time
from chart.utils.echarts_plot import kline_pro
from pyecharts.charts import Bar, Tab
from chart.utils.KlineGenerator import KlineGenerator


def main1():
    datafeed = get_datafeed()
    # symbol: str=''
    # exchange: Exchange=Exchange.CFFEX
    # start: datetime=
    # end: datetime = None
    # interval: Interval = Interval.MINUTE
    # req = HistoryRequest(
    #     symbol='600809',
    #     exchange=Exchange.SSE,
    #     interval=Interval.MINUTE,
    #     start=datetime(2021, 11, 1),
    #     end=datetime(2021, 11, 10)
    # )
    # bars = datafeed.query_bar_history(req)
    # print(bars)
    # end_dt = datetime.now()
    # symbol = '600809.XSHG'
    #
    # kg = KlineGenerator()
    # map = {'1d': bars}
    # [kg.init_from_db(k, map[k]) for k in map]
    #
    # tab = Tab(page_title="{}@{}".format(symbol, end_dt.strftime("%Y-%m-%d %H:%M")))
    #
    # for freq in kg.freqs:
    #     kline = kg.get_all_kline(freq)
    #     print(freq + ":" + str(len(kline)))
    #     jc = JChan(engine=None, setting={}, strategy_name='jchan', vt_symbol='600809')
    #     for bar in kline:
    #         jc.on_bar(bar)
    #
    #     b1 = []
    #     b2 = []
    #     b3 = []
    #     s1 = []
    #     s2 = []
    #     s3 = []
    #
    #     bi = []
    #     print(jc.stroke_list)
    #     for i in jc.stroke_list:
    #         price = i[1]
    #         if i[3] == 'up':
    #             price = i[0]
    #
    #         bi.append({
    #             'dt': i[2],
    #             'bi': price
    #         })
    #
    #     # kline = [x.__dict__ for x in kg.get_all_kline(freq)]
    #     print(jc.stroke_macd)
    #     print(jc.trend_list)
    #     kline = [x.__dict__ for x in jc.chan_k_list]
    #     chart = kline_pro(kline, bi=bi, zs=jc.pivot_list)
    #     tab.add(chart, freq)
    # tab.render('test.html')


if __name__ == '__main__':
    # set_token(token='r_atbJBC_zlpqbzepTwi4c0s4F0dkJ0KHtdQnMgJDK0bQRAX8t8P0YlNj3si_f4s')
    # s=stock_list()
    # print(s)
    main1()

    # bar = stock_quote_minutes("600519.SH", "2021-8-9", "2021-10-1")
    # print(bar)
