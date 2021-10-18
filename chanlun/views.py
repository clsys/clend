import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from trade.models import Trade
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from time import sleep

# Create your views here.
def index(request):
    trade = Trade()
    trade.userid = '666'
    trade.stock_id = '600519'
    trade.trade_type = 'backtest'
    trade.type = '2b'
    trade.trade_time = timezone.now()
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


def room(request, room_name):
    return render(request, 'index.html', {
        'room_name': room_name
    })

def dizzy(request):
    print("dizzy start")
    sleep(10)
    print("dizzy end")
    return HttpResponse('sleep ok')

def start(request):
    channel_layer = get_channel_layer()

    for i in range(100):
        sleep(1)
        async_to_sync(channel_layer.group_send)("chat_table", {"type": "chat_message", "message": 'hello ' + str(i)})
        # channel_layer.group_send(
        #     'chat_table',
        #     {"type": "chat.system_message", "text": 'hello ' + str(i)},
        # )
    return HttpResponse('ok')
