from django.db import models


# Create your models here.
class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=90)
    stock_id = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=10)
    type = models.CharField(max_length=2)
    trade_time = models.DateTimeField(auto_now_add=True)
    trade_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.IntegerField()
    total_money = models.DecimalField(max_digits=10, decimal_places=2)
    cur_funds = models.DecimalField(max_digits=10, decimal_places=2)
    origin_funds = models.DecimalField(max_digits=10, decimal_places=2)
    after_position = models.IntegerField()
    before_position = models.IntegerField()
    is_success = models.CharField(max_length=1, default='Y')
    order_id = models.IntegerField()

    class Meta:
        db_table = 'cl_trade'


class Gain(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=90)
    stock_id = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=10)
    origin_position = models.IntegerField()
    origin_price = models.DecimalField(max_digits=10, decimal_places=2)
    cur_position = models.IntegerField()
    cur_price = models.DecimalField(max_digits=10, decimal_places=2)
    origin_funds = models.DecimalField(max_digits=10, decimal_places=2)
    cur_funds = models.DecimalField(max_digits=10, decimal_places=2)
    current_equity = models.DecimalField(max_digits=10, decimal_places=2)
    update_time = models.DateTimeField(auto_now_add=True)
    order_id = models.IntegerField()

    class Meta:
        db_table = 'cl_gain'


class UserSub(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=90)
    update_time = models.DateTimeField(auto_now_add=True)
    valid = models.CharField(max_length=1)
    order_id = models.IntegerField()

    class Meta:
        db_table = 'cl_user_sub'


class Log(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    log = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cl_log'
