from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from django.http import HttpResponse
from chart.constant import freq_inv, Freq, freq_db
from chart.utils.KlineGenerator import KlineGenerator
from datetime import datetime
import redis
from jqdatasdk import *
from chart.objects import RawBar

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./chart/templates"))
from pyecharts import options as opts
from pyecharts.charts import Bar, Tab
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
# from chart.kline import get_kline
from chart.utils.echarts_plot import kline_pro
from chart.utils.tools import raw_data_to_array
from chart.chanlun import calculate_bs
from chart.services.service import Service
from chart.services.Barfromdb import BarFromDb
from chanlun.strategies.mychan import JChan
from chart.constant import freq_map
from clend.settings import SETTINGS
bfd = BarFromDb()
service = Service()


def index(request):
    c = (
        Bar()
            .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
            .add_yaxis("商家B", [15, 25, 16, 55, 48, 8])
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
    )
    return HttpResponse(c.render_embed())


max_count = 20
max_len = 0
inited = False

auth(SETTINGS["jq.username"], SETTINGS["jq.password"])  # 账号是申请时所填写的手机号；密码为聚宽官网登录密码，新申请用户默认为手机号后6位

def cache_get(key):
    r = redis.Redis(host='127.0.0.1', port=6379)
    return r.get(key)


def cache_set(key, data):
    r = redis.Redis(host='127.0.0.1', port=6379)
    r.set(key, data)


def kline_from_jq(symbol, end, freq='1m', count=2000):
    use_count = get_query_count()
    if use_count['spare'] <= 0:
        return None
    df = get_bars(symbol, count, unit=freq, fields=['date', 'open', 'close', 'high', 'low', 'volume', 'money'],
                  include_now=False, end_dt=end.strftime("%Y-%m-%d"))
    ret = []
    id = 0
    for index, k in df.iterrows():
        id += 1
        ret.append(RawBar(symbol=symbol, dt=k['date'], id=id, freq=freq_map[freq],
                          open=round(float(k['open']), 2),
                          close=round(float(k['close']), 2),
                          high=round(k['high'], 2),
                          low=round(k['low'], 2),
                          vol=int(k['volume'])))
    return ret


# def init(symbol, end_dt):
#     global inited, max_count, max_len
#
#     if not inited:
#         kg = KlineGenerator(max_count=max_count * 2)
#         # klines = kg.get_klines({k: 3000 for k in kg.freqs})
#         for freq in kg.freqs:
#             bars = get_kline(symbol, end_date=end_dt, freq=freq_inv[freq], count=max_count)
#             max_len = len(bars)
#             print('max_len: ' + str(max_len))
#             kg.init_kline(freq, bars)
#     return kg


# def kline(request):
#     symbol = request.GET['symbol']
#     if not symbol:
#         return HttpResponse("None")
#     global inited, max_count, max_len
#     end_dt = datetime.now()
#     if max_count < max_len:
#         max_count += 100
#     kg = init(symbol, end_dt)
#     tab = Tab(page_title="{}@{}".format(symbol, end_dt.strftime("%Y-%m-%d %H:%M")))
#     for freq in kg.freqs:
#         kline = [x.__dict__ for x in kg.get_kline(freq, max_count)]
#         chart = kline_pro(kline)
#         tab.add(chart, freq)
#     return HttpResponse(tab.render_embed())


# def init_bar(symbol, end_dt):
#     kg = KlineGenerator(max_count=max_count * 2)
#     # klines = kg.get_klines({k: 3000 for k in kg.freqs})
#     bars = get_kline(symbol, end_date=end_dt, count=max_count)
#     max_len = len(bars)
#     print("max_len: " + str(max_len))
#     for i in bars:
#         i.freq = Freq.F1
#         kg.update(i)
#     print("m1_len: " + str(len(kg.m1)))
#     return kg

def init_bar_from_jq(symbol):
    kg = KlineGenerator()
    map = {freq_db[k]: kline_from_jq(symbol, datetime.now(), freq_db[k]) for k in kg.freqs}
    [kg.init_from_db(k, map[k]) for k in map]
    return kg


def init_bar_from_db(symbol):
    kg = KlineGenerator()
    map = {freq_db[k]: bfd.get(freq_db[k], symbol) for k in kg.freqs}
    [kg.init_from_db(k, map[k]) for k in map]
    return kg


def chan1(request):
    # symbol = request.GET['symbol']
    # if not symbol:
    #     return HttpResponse("None")
    end_dt = datetime.now()
    # kg = init_bar(symbol, end_dt)
    symbol = '600809.XSHG'
    kg = init_bar_from_db(symbol)
    tab = Tab(page_title="{}@{}".format(symbol, end_dt.strftime("%Y-%m-%d %H:%M")))

    for freq in kg.freqs:
        kline = kg.get_all_kline(freq)
        print(freq + ":" + str(len(kline)))
        klist = raw_data_to_array(kline)
        strokesList, lineList, pivotList, buy_list, sell_list, buy_list_history, sell_list_history = calculate_bs(klist)
        bs = []
        for i in buy_list:
            bs.append({
                'dt': i[0],
                'mark': 'buy',
                'price': i[1]
            })
        for i in sell_list:
            bs.append({
                'dt': i[0],
                'mark': 'sell',
                'price': i[1]
            })
        bi = []
        for i in strokesList:
            bi.append({
                'dt': i[0],
                'bi': i[1]
            })
        xd = []
        for i in lineList:
            xd.append({
                'dt': i[0],
                'xd': i[1]
            })
        kline = [x.__dict__ for x in kg.get_all_kline(freq)]
        chart = kline_pro(kline, bi=bi, xd=xd, zs=pivotList,
                          bs=bs)
        tab.add(chart, freq)
    return HttpResponse(tab.render_embed())


def lun(request):
    # symbol = request.GET['symbol']
    # if not symbol:
    #     return HttpResponse("None")
    end_dt = datetime.now()
    # kg = init_bar(symbol, end_dt)
    symbol = '600809.XSHG'
    kg = init_bar_from_db(symbol)
    tab = Tab(page_title="{}@{}".format(symbol, end_dt.strftime("%Y-%m-%d %H:%M")))

    for freq in kg.freqs:
        kline = kg.get_all_kline(freq)
        print(freq + ":" + str(len(kline)))
        klist = raw_data_to_array(kline)
        strokesList, lineList, pivotList, buy_list, sell_list, buy_list_history, sell_list_history = calculate_bs(klist)
        if freq == "1分钟":
            print(pivotList)
        b1 = []
        b2 = []
        b3 = []
        s1 = []
        s2 = []
        s3 = []
        for i in buy_list:
            if i[2] == "B1":
                b1.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })
            if i[2] == "B2":
                b2.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })
            if i[2] == "B3":
                b3.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })

        for i in sell_list:
            if i[2] == "S1":
                s1.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
            if i[2] == "S2":
                s2.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
            if i[2] == "S3":
                s3.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
        bi = []
        for i in strokesList:
            bi.append({
                'dt': i[0],
                'bi': i[1]
            })
        xd = []
        for i in lineList:
            xd.append({
                'dt': i[0],
                'xd': i[1]
            })
        kline = [x.__dict__ for x in kg.get_all_kline(freq)]
        chart = kline_pro(kline, bi=bi, xd=xd, zs=pivotList, b1=b1, b2=b2, b3=b3, s1=s1, s2=s2, s3=s3)
        tab.add(chart, freq)
    return HttpResponse(tab.render_embed())


# http://localhost:8000/chart/chan?include=True&line=True&symbol=600519.XSHG
def chan(request):
    symbol = request.GET['symbol']
    include = request.GET['include']
    if include == 'True':
        include = True
    else:
        include = False
    line = request.GET['line']
    if line == 'True':
        line = True
    else:
        line = False
    end_dt = datetime.now()
    # kg = init_bar(symbol, end_dt)
    # symbol = '600809.XSHG'
    kg = None
    if symbol == '600809.XSHG':
        kg = init_bar_from_db(symbol)
    else:
        kg = init_bar_from_jq(symbol)
    tab = Tab(page_title="{}@{}".format(symbol, end_dt.strftime("%Y-%m-%d %H:%M")))

    for freq in kg.freqs:
        kline = kg.get_all_kline(freq)
        print(freq + ":" + str(len(kline)))
        jc = JChan(engine=None, setting={}, strategy_name='jchan', vt_symbol='600809', include=include,
                   build_pivot=line)
        # print(kline)
        for bar in kline:
            jc.on_bar(bar)

        b1 = []
        b2 = []
        b3 = []
        s1 = []
        s2 = []
        s3 = []
        x_b1 = []
        x_b2 = []
        x_b3 = []
        x_s1 = []
        x_s2 = []
        x_s3 = []
        bi = []
        # print(jc.stroke_list)
        for i in jc.stroke_list:
            price = i[1]
            if i[3] == 'up':
                price = i[0]

            bi.append({
                'dt': i[2],
                'bi': price
            })

        xd = []
        for i in jc.line_list:
            price = i[1]
            if i[3] == 'up':
                price = i[0]

            xd.append({
                'dt': i[2],
                'xd': price
            })
        for i in jc.buy_list:
            if i[2] == "B1":
                b1.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })
            if i[2] == "B2":
                b2.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })
            if i[2] == "B3":
                b3.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })

        for i in jc.sell_list:
            if i[2] == "S1":
                s1.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
            if i[2] == "S2":
                s2.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
            if i[2] == "S3":
                s3.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
        for i in jc.x_buy_list:
            if i[2] == "B1":
                x_b1.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })
            if i[2] == "B2":
                x_b2.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })
            if i[2] == "B3":
                x_b3.append({
                    'dt': i[0],
                    'mark': 'buy',
                    'price': i[1]
                })

        for i in jc.x_sell_list:
            if i[2] == "S1":
                x_s1.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
            if i[2] == "S2":
                x_s2.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
            if i[2] == "S3":
                x_s3.append({
                    'dt': i[0],
                    'mark': 'sell',
                    'price': i[1]
                })
        # kline = [x.__dict__ for x in kg.get_all_kline(freq)]
        # print('jc.macd')
        # print(jc.macd)
        # print('jc.trend_list')
        # print(jc.trend_list)
        kline = [x.__dict__ for x in jc.chan_k_list]
        chart = kline_pro(kline, bi=bi, xd=xd, zs=jc.pivot_list, b1=b1, b2=b2, b3=b3, s1=s1, s2=s2, s3=s3, x_b1=x_b1,
                          x_b2=x_b2, x_b3=x_b3, x_s1=x_s1, x_s2=x_s2, x_s3=x_s3)
        # chart = kline_pro(kline, bi=bi, xd=xd, zs=jc.pivot_list)
        tab.add(chart, freq)
    return HttpResponse(tab.render_embed())


def query(request):
    return HttpResponse(bfd.get(request.GET['freq']))


# http://localhost:8000/chart/new_gain?userid=1d&stock_id=600809.XSHG&trade_type=realtime
def new_gain(request):
    return HttpResponse(
        service.create_new_gain(request.GET['userid'], request.GET['stock_id'], request.GET['trade_type']))
