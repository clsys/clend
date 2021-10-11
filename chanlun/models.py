from django.db import models


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
