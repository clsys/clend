from django.db import models
from datetime import datetime

# Create your models here.
class Strategy(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=90)
    code = models.CharField(max_length=10)
    lang = models.CharField(max_length=10, default='python')
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cl_strategy'


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=90)
    # real or backtest
    order_type = models.CharField(max_length=10)
    total_money = models.DecimalField(max_digits=10, decimal_places=2)
    # bar:5m,30m,1h,1d tick
    type = models.CharField(max_length=2)
    lang = models.CharField(max_length=10, default='python')

    # order time for exception situation
    start_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', null=True)
    end_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', null=True)
    cur_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', null=True)

    # order create and change time
    create_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', null=True)
    update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)

    class Meta:
        db_table = 'cl_order'

    class DbBarData(models.Model):
        id = models.AutoField(primary_key=True)
        symbol: str = models.CharField(max_length=255)
        exchange: str = models.CharField(max_length=255)
        datetime: datetime = models.DateTimeField()
        interval: str = models.CharField(max_length=255)

        volume: float = models.FloatField()
        open_interest: float = models.FloatField()
        open_price: float = models.FloatField()
        high_price: float = models.FloatField()
        low_price: float = models.FloatField()
        close_price: float = models.FloatField()

        class Meta:
            db_table = 'dbbardata'

    class DbTickData(models.Model):
        id = models.AutoField(primary_key=True)
        symbol: str = models.CharField(max_length=255)
        exchange: str = models.CharField(max_length=255)
        datetime: datetime = models.DateTimeField()

        name: str = models.CharField(max_length=255)
        volume: float = models.FloatField()
        open_interest: float = models.FloatField()
        last_price: float = models.FloatField()
        last_volume: float = models.FloatField()
        limit_up: float = models.FloatField()
        limit_down: float = models.FloatField()

        open_price: float = models.FloatField()
        high_price: float = models.FloatField()
        low_price: float = models.FloatField()
        pre_close: float = models.FloatField()

        bid_price_1: float = models.FloatField()
        bid_price_2: float = models.FloatField(null=True)
        bid_price_3: float = models.FloatField(null=True)
        bid_price_4: float = models.FloatField(null=True)
        bid_price_5: float = models.FloatField(null=True)

        ask_price_1: float = models.FloatField()
        ask_price_2: float = models.FloatField(null=True)
        ask_price_3: float = models.FloatField(null=True)
        ask_price_4: float = models.FloatField(null=True)
        ask_price_5: float = models.FloatField(null=True)

        bid_volume_1: float = models.FloatField()
        bid_volume_2: float = models.FloatField(null=True)
        bid_volume_3: float = models.FloatField(null=True)
        bid_volume_4: float = models.FloatField(null=True)
        bid_volume_5: float = models.FloatField(null=True)

        ask_volume_1: float = models.FloatField()
        ask_volume_2: float = models.FloatField(null=True)
        ask_volume_3: float = models.FloatField(null=True)
        ask_volume_4: float = models.FloatField(null=True)
        ask_volume_5: float = models.FloatField(null=True)

        class Meta:
            db_table = 'dbtickdata'