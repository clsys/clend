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
from django.db.models import Q
from clend.utils import handle_db_connections

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


cur = str(datetime.now().date())
start_sw = datetime.strptime(str(datetime.now().date()) + " 9:30", '%Y-%m-%d %H:%M')
end_sw = datetime.strptime(str(datetime.now().date()) + " 11:30", '%Y-%m-%d %H:%M')

start_xw = datetime.strptime(str(datetime.now().date()) + " 13:00", '%Y-%m-%d %H:%M')
end_xw = datetime.strptime(str(datetime.now().date()) + " 15:00", '%Y-%m-%d %H:%M')
# 每天初始化flag
inited = False

user_list = ['1m', '5m', '15m', '30m', '60m', '1d']
symbol_list = ['600809.XSHG']
match = {'1分钟': '1m', '5分钟': '5m', '15分钟': '15m', '30分钟': '30m', '60分钟': '60m', '1天': '1d', '日线': '1d'}
match_point = {'1m': '1分钟', '5m': '5分钟', '15m': '15分钟', '30m': '30分钟', '60m': '60分钟', '1d': '1天', '1d': '日线'}
# match_days = {'1m': 2, '5m': 4, '15m': 12, '30m': 24, '60m': 48, '1d': 192}
# match_days = {'1m': 4, '5m': 40, '15m': 125, '30m': 250, '60m': 500, '1d': 2000}
match_days = {'1m': 2, '5m': 20, '15m': 60, '30m': 120, '60m': 250, '1d': 1000}
mp = {}


def get_last_to_now_point(gain):
    if not gain or not gain.userid:
        return
    list_freq_stock_id = gain.userid.split('.', 1)
    # 每天系统 获取买卖点的周期、范围
    start_t = datetime.now().date() - timedelta(days=match_days[list_freq_stock_id[0]])
    query = Point.objects.filter(
        Q(stock_id=list_freq_stock_id[1]) & Q(point__gt=start_t) & Q(level=match_point[list_freq_stock_id[0]]))
    return query


def check_bs(gain):
    global mp
    bsset = None
    invalid_bsset = None
    valid_key = gain.userid + '-valid'
    invalid_key = gain.userid + '-invalid'
    if valid_key in mp.keys():
        bsset = mp[valid_key]
    if invalid_key in mp.keys():
        invalid_bsset = mp[invalid_key]

    query = get_last_to_now_point(gain)
    cur_set = set()
    cur_invalid_set = set()
    bs_list = []
    invalid_bs_list = []
    for i in query:
        if i.invalid_time:
            cur_invalid_set.add(i)
    for i in query:
        if not i.invalid_time and not cur_invalid_set.__contains__(i):
            cur_set.add(i)
    if bsset == None:
        l_point = list(cur_set)
        l_point.sort(key=lambda x: x.point)
        print(f"#########################{gain.userid}-valid: inited#########################")
        for i in l_point:
            print(i.stock_id + ":" + i.point.strftime('%Y-%m-%d %H:%M') + ":" + i.level + ":" + i.type)
        print(f"#########################{gain.userid}-valid: inited#########################")
    else:
        bs_diff = cur_set - bsset
        bs_list = list(bs_diff)
        bs_list.sort(key=lambda x: x.point)
        for last in bs_list:
            print("valid_bs: " + last.stock_id + ":" + last.point.strftime(
                '%Y-%m-%d %H:%M') + ":" + last.level + ":" + last.type)

    if invalid_bsset == None:
        l_point = list(cur_invalid_set)
        l_point.sort(key=lambda x: x.point)
        print(f"#########################{gain.userid}-invalid: inited#########################")
        for i in l_point:
            print(i.stock_id + ":" + i.point.strftime('%Y-%m-%d %H:%M') + ":" + i.level + ":" + i.type)
        print(f"#########################{gain.userid}-invalid: inited#########################")
    else:
        invalid_bs_diff = cur_invalid_set - invalid_bsset
        cur_invalid_list = list(cur_invalid_set)
        cur_invalid_list.sort(key=lambda x: x.point)
        print(cur_invalid_list)
        invalid_bsset_list = list(invalid_bsset)
        invalid_bsset_list.sort(key=lambda x: x.point)
        print(invalid_bsset_list)

        invalid_bs_list = list(invalid_bs_diff)
        invalid_bs_list.sort(key=lambda x: x.point)
        for last in invalid_bs_list:
            print("invalid_bs: " + last.stock_id + ":" + last.point.strftime(
                '%Y-%m-%d %H:%M') + ":" + last.level + ":" + last.type)

    mp[valid_key] = cur_set
    mp[invalid_key] = cur_invalid_set
    return bs_list, invalid_bs_list


def update_gain(gain, trade, bar, type):
    gain.cur_price = bar.close
    gain.update_time = datetime.now()
    gain.current_equity = gain.cur_funds + decimal.Decimal(
        gain.cur_price * (gain.cur_position + gain.today_position)) - gain.origin_funds - decimal.Decimal(
        gain.origin_position * gain.origin_price)

    if type:
        gain.cur_funds = trade.cur_funds
        if type == 'buy':
            gain.today_position = gain.today_position + trade.unit

        elif type == 'sell':
            gain.cur_position = gain.cur_position - trade.unit

    gain.save()


def update_last_position(gain):
    gain.cur_position = gain.cur_position + gain.today_position
    gain.today_position = 0
    gain.save()


def get_cur_gain(userid):
    query = Gain.objects.filter(userid=userid)
    if len(query) > 0:
        return query[0]


def buy_sell(gain, bs, unit, bar, type):
    global start_sw, end_sw, start_xw, end_xw
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
    trade.total_money = decimal.Decimal(bar.close * trade.unit)
    trade.before_position = gain.cur_position
    trade.origin_funds = trade.cur_funds
    trade.is_success = 'Y'
    if bs.invalid_time:
        if bs.type.startswith('S'):
            trade.type = bs.type.replace('S', 'B')
        else:
            trade.type = bs.type.replace('B', 'S')

    if not bs.invalid_time and not ((start_sw <= bs.point <= end_sw) or (start_xw <= bs.point <= end_xw)) and bs.level=='1分钟':
        bs_time = bs.point.strftime('%Y-%m-%d %H:%M:%S')
        trade.is_success = 'N'
        trade.reason = f'买卖点有误，时间：{bs_time},不在有效时间范围内，不能交易'
    if type == 'buy':
        trade.cur_funds = gain.cur_funds - trade.total_money
        if trade.cur_funds < 0:
            trade.is_success = 'N'
            trade.reason = f'资金不足: {trade.cur_funds}，买单无法交易'
        trade.after_position = gain.cur_position + gain.today_position + trade.unit
    else:
        trade.cur_funds = gain.cur_funds + trade.total_money
        trade.after_position = gain.cur_position - trade.unit
        if trade.after_position < 0:
            trade.is_success = 'N'
            trade.reason = f'头寸不足:{trade.after_position}，卖单无法交易'
        trade.after_position = trade.after_position + gain.today_position
    if trade.unit <= 0:
        trade.is_success = 'N'
        trade.reason = f'交易头寸错误:{trade.unit}'
    trade.save()
    if trade.is_success == 'Y':
        update_gain(gain, trade, bar, type)


def trade(gain, symbol, bar):
    bs_list, invalid_bs_list = check_bs(gain)
    update_gain(gain, None, bar, None)

    for bs in bs_list:
        # 当前级别和买卖点级别不匹配
        if not gain.userid.startswith(match[bs.level]):
            return
        if bs.type == 'B1':
            factor = decimal.Decimal('0.01')
            buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'buy')
        if bs.type == 'B2':
            factor = decimal.Decimal('0.02')
            buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'buy')
        if bs.type == 'B3':
            factor = decimal.Decimal('0.02')
            buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'buy')
        if bs.type == 'S1':
            factor = decimal.Decimal('0.01')
            buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'sell')
        if bs.type == 'S2':
            factor = decimal.Decimal('0.02')
            buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'sell')
        if bs.type == 'S3':
            factor = decimal.Decimal('0.02')
            buy_sell(gain, bs, int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'sell')
    for invalid_bs in invalid_bs_list:
        # 当前级别和买卖点级别不匹配
        if not gain.userid.startswith(match[invalid_bs.level]):
            return
        if invalid_bs.type == 'B1':
            factor = decimal.Decimal('0.01')
            buy_sell(gain, invalid_bs,
                     int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'sell')
        if invalid_bs.type == 'B2':
            factor = decimal.Decimal('0.02')
            buy_sell(gain, invalid_bs,
                     int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'sell')
        if invalid_bs.type == 'B3':
            factor = decimal.Decimal('0.02')
            buy_sell(gain, invalid_bs,
                     int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'sell')
        if invalid_bs.type == 'S1':
            factor = decimal.Decimal('0.01')
            buy_sell(gain, invalid_bs,
                     int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'buy')
        if invalid_bs.type == 'S2':
            factor = decimal.Decimal('0.02')
            buy_sell(gain, invalid_bs,
                     int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'buy')
        if invalid_bs.type == 'S3':
            factor = decimal.Decimal('0.02')
            buy_sell(gain, invalid_bs,
                     int(gain.cur_funds * factor / decimal.Decimal(bar.close) / decimal.Decimal('100.0')),
                     bar,
                     'buy')


# 系统只初始化一次
@handle_db_connections
def init_sys():
    global user_list, symbol_list
    start = datetime.now()
    for symbol in symbol_list:
        for user in user_list:
            gain = get_cur_gain(user + "." + symbol)
            check_bs(gain)
            bar = bfd.get_latest_bar(user, symbol)
            if gain and not gain.cur_funds and not gain.cur_position:
                gain.cur_funds = gain.origin_funds
                gain.cur_position = gain.origin_position
                gain.origin_price = bar.close
                gain.cur_price = bar.close
                gain.save()
    end = datetime.now()
    print('init sys takes time: ' + str(end - start))


init_sys()


@handle_db_connections
def task():
    global bsset, start_sw, end_sw, start_xw, end_xw, cur, user_list, symbol_list
    now = datetime.now()
    now_str = str(now.date())
    if cur != now_str:
        # 每天更新买卖点集合
        start_sw = datetime.strptime(now_str + " 9:30", '%Y-%m-%d %H:%M')
        end_sw = datetime.strptime(now_str + " 11:30", '%Y-%m-%d %H:%M')
        start_xw = datetime.strptime(now_str + " 13:00", '%Y-%m-%d %H:%M')
        end_xw = datetime.strptime(now_str + " 15:00", '%Y-%m-%d %H:%M')
        cur = now_str

        # 将昨天的仓位更新到今天
        for symbol in symbol_list:
            for user in user_list:
                gain = get_cur_gain(user + "." + symbol)
                update_last_position(gain)

    # 交易时间进行交易
    if (start_sw <= now <= end_sw) or (start_xw <= now <= end_xw):
        for symbol in symbol_list:
            for user in user_list:
                gain = get_cur_gain(user + "." + symbol)
                bar = bfd.get_latest_bar(user, symbol)
                if bar.dt.strftime("%Y-%m-%d") == now.strftime("%Y-%m-%d"):
                    trade(gain, symbol, bar)


from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
# scheduler.add_job(task, 'interval', seconds=1)
scheduler.add_job(task, 'interval', minutes=1)
scheduler.start()
