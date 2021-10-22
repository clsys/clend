from django.http import HttpResponse
from django.shortcuts import render
import decimal
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from time import sleep
from chanlun.hsdata import Data
from chart.models import *
from chart.views import bfd

data = Data()


def init(request):
    gain = Gain()
    gain.userid = '666'
    gain.stock_id = ''
    gain.cur_funds = ''
    gain.origin_funds = ''
    gain.trade_type = ''
    gain.cur_position = ''
    gain.cur_price = ''
    gain.current_equity = ''

    return HttpResponse("Hello, world. You're at the polls index.")


# Create your views here.
def index1(request):
    trade = Trade()
    trade.userid = '666'
    trade.stock_id = '600519'
    trade.trade_type = 'backtest'
    trade.type = '2b'
    trade.trade_time = datetime.now()
    trade.trade_price = 10.2
    trade.unit = 22
    trade.order_id = '666'
    trade.total_money = 100.2
    trade.cur_funds = 100.2
    trade.origin_funds = 100.2
    trade.before_position = 102
    trade.after_position = 103
    trade.is_success = 'Y'
    trade.save()

    return HttpResponse("Hello, world. You're at the polls index.")


# 创建新账号
# http://10.28.239.80:8000/chart/new_gain?userid=666&stock_id=600809.SH&trade_type=realtime
# 不是这个接口
def index(request):
    userid = '666'
    gain = get_cur_gain(userid)
    if not gain.cur_funds:
        gain.cur_funds = 10000000
        gain.origin_funds = 0
        gain.cur_position = 0
        gain.origin_position = 0
        gain.save()
    return HttpResponse("ok")


def room(request, room_name):
    return render(request, 'index.html', {
        'room_name': room_name
    })


def dizzy(request):
    print("dizzy start")
    sleep(10)
    print("dizzy end")
    return HttpResponse('sleep ok')


def ks(request):
    channel_layer = get_channel_layer()

    for i in range(100):
        sleep(1)
        async_to_sync(channel_layer.group_send)("chat_table", {"type": "chat_message", "message": 'hello ' + str(i)})
        # channel_layer.group_send(
        #     'chat_table',
        #     {"type": "chat.system_message", "text": 'hello ' + str(i)},
        # )
    return HttpResponse('ok')


def get_bars(request):
    if request.method != 'GET':
        return HttpResponse('method error')
    symbol = request.GET.get("symbol")
    datalen = request.GET.get("datalen")
    day = request.GET.get("day")
    unit = request.GET.get("unit")
    if not symbol or not datalen or not day or not unit:
        return HttpResponse(None)
    # return HttpResponse(data.get_bars(symbol, datalen, day, unit))
    return HttpResponse(data.get_bars('000028.SZ', 10, '2021-10-20', '1m'))


def get_all_securities(request):
    if request.method != 'GET':
        return HttpResponse('method error')
    date = request.GET.get("date")
    return HttpResponse(data.get_all_securities(date))


bsset = set()
cur = str(datetime.now().date())
start = datetime.strptime(str(datetime.now().date()) + " 9:30", '%Y-%m-%d %H:%M')
end = datetime.strptime(str(datetime.now().date()) + " 15:00", '%Y-%m-%d %H:%M')
inited = False


def check_bs():
    global bsset, start, end, inited
    start_t = datetime.now() - timedelta(hours=24)
    query = Point.objects.filter(point__gt=start_t)
    cur_set = set()
    last = None
    for i in query:
        cur_set.add(i)
    if len(bsset) != len(cur_set):
        l_point = list(cur_set)
        l_point.sort(key=lambda x: x.point)
        if not inited:
            # SELECT DISTINCT stock_id, level, point FROM chanlun.cl_point_result where point > '2021-10-21' order by point;
            print("#########################inited#########################")
            for i in l_point:
                print(i.stock_id + ":" + i.point.strftime('%Y-%m-%d %H:%M') + ":" + i.level + ":" + i.type)
            print("#########################inited#########################")
            inited = True
        else:
            last = list[-1]
            print(last.stock_id + ":" + last.point.strftime('%Y-%m-%d %H:%M') + ":" + last.level + ":" + last.type)
        bsset = cur_set
        return last


def update_gain(gain, trade, bar, type):
    gain.origin_funds = gain.cur_funds
    gain.origin_position = gain.cur_position
    gain.origin_price = gain.cur_price
    gain.cur_price = bar.close
    if type == 'buy':
        gain.cur_position = gain.cur_position + trade.unit
        gain.cur_funds = gain.cur_funds - trade.cur_funds

    else:
        gain.cur_position = gain.cur_position + trade.unit
        gain.cur_funds = gain.cur_funds + trade.cur_funds

    gain.current_equity = gain.cur_funds + decimal.Decimal(bar.close * gain.cur_position) - gain.origin_funds
    gain.save()


def get_cur_gain(userid):
    query = Gain.objects.filter(userid=userid)
    if len(query) > 0:
        return query[0]


def buy_sell(gain, bs, unit, bar, type):
    trade = Trade()
    trade.userid = gain.userid
    trade.stock_id = bs.stock_id
    trade.trade_type = 'realtime'
    trade.type = bs.type
    trade.trade_time = datetime.now()
    trade.bs_time = bs.point
    trade.level = bs.level
    trade.trade_price = bar.close
    trade.unit = unit * 100
    trade.total_money = decimal.Decimal(bar.close * unit)
    trade.origin_funds = gain.cur_funds
    trade.before_position = gain.cur_position

    trade.is_success = 'Y'
    if type == 'buy':
        trade.cur_funds = gain.cur_funds - trade.total_money
        if trade.cur_funds < 0:
            trade.is_success = 'N'
            trade.reason = '资金不足，买单无法交易'
        trade.after_position = gain.cur_position + unit
    else:
        trade.cur_funds = gain.cur_funds + trade.total_money
        trade.after_position = gain.cur_position - unit
        if trade.after_position < 0:
            trade.is_success = 'N'
            trade.reason = '头寸太大，卖单无法交易'
    if trade.unit == 0:
        trade.is_success = 'N'
        trade.reason = '购买头寸是0'
    trade.save()
    if trade.is_success == 'Y':
        update_gain(gain, trade, bar, type)


def trade():
    symbol = '600809.XSHG'
    userid = '666'
    gain = get_cur_gain(userid)
    lbar = bfd.get_latest_1m_bar('1m', symbol)
    bs = check_bs()
    if not bs:
        return
    if bs.type == 'B1':
        factor = decimal.Decimal('0.01')
        buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(lbar.close)), lbar, 'buy')
    if bs.type == 'B2':
        factor = decimal.Decimal('0.02')
        buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(lbar.close)), lbar, 'buy')
    if bs.type == 'B3':
        factor = decimal.Decimal('0.02')
        buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(lbar.close)), lbar, 'buy')
    if bs.type == 'S1':
        factor = decimal.Decimal('0.01')
        buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(lbar.close)), lbar, 'sell')
    if bs.type == 'S2':
        factor = decimal.Decimal('0.02')
        buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(lbar.close)), lbar, 'sell')
    if bs.type == 'S3':
        factor = decimal.Decimal('0.02')
        buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(lbar.close)), lbar, 'sell')


def task():
    global bsset, start, end, cur
    now = datetime.now()
    now_str = str(now.date())
    if cur != now_str:
        start = datetime.strptime(now_str + " 9:30", '%Y-%m-%d %H:%M')
        end = datetime.strptime(now_str + " 15:00", '%Y-%m-%d %H:%M')
        bsset.clear()
    if now >= start and now <= end:
        trade()


from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
# scheduler.add_job(task, 'interval', seconds=1)
scheduler.add_job(task, 'interval', minutes=1)
scheduler.start()
