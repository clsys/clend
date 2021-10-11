from django.http import HttpResponse
from trade.models import Trade
from django.utils import timezone


# Create your views here.
def index(request):
    trade = Trade()
    trade.userid='666'
    trade.stock_id = '600519'
    trade.trade_type = 'backtest'
    trade.type='2b'
    trade.trade_time = timezone.now()
    trade.trade_price=10.2
    trade.unit=22
    trade.total_money=100.2
    trade.cur_funds=100.2
    trade.origin_funds=100.2
    trade.before_position=102
    trade.after_position=103
    trade.isSuccess='Y'
    trade.save()

    return HttpResponse("Hello, world. You're at the polls index.")