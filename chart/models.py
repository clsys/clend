from django.db import models
from datetime import datetime


# Create your models here.
class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=90)
    stock_id = models.CharField(max_length=20)
    trade_type = models.CharField(max_length=10)
    type = models.CharField(max_length=2, null=True)
    bs_time = models.DateTimeField(null=True)
    level = models.CharField(max_length=10)
    trade_time = models.DateTimeField(auto_now_add=True, null=True)
    trade_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit = models.IntegerField(null=True)
    total_money = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cur_funds = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    origin_funds = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    after_position = models.IntegerField(null=True)
    before_position = models.IntegerField(null=True)
    is_success = models.CharField(max_length=1, default='Y', null=True)
    reason = models.CharField(max_length=90, null=True)

    class Meta:
        db_table = 'cl_trade'


class Gain(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=90, unique=True)
    stock_id = models.CharField(max_length=20)
    trade_type = models.CharField(max_length=10)
    origin_position = models.IntegerField(null=True)
    origin_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cur_position = models.IntegerField(null=True)
    today_position = models.IntegerField(null=True)
    cur_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    origin_funds = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cur_funds = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    current_equity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cl_gain'


class Point(models.Model):
    id = models.AutoField(primary_key=True)
    stock_id = models.CharField(max_length=20)
    level = models.CharField(max_length=10, null=True)
    point = models.DateTimeField(null=True)
    type = models.CharField(max_length=2, null=True)
    evaluation_time = models.DateTimeField(null=True)
    valid = models.SmallIntegerField(null=True)
    invalid_time = models.DateTimeField(null=True)
    high = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __hash__(self):
        return hash((self.stock_id, self.level, self.point.strftime('%Y-%m-%d %H:%M'), self.type))

    def __repr__(self):
        return f'point: {self.stock_id}, {self.level}, {self.point}, {self.type}'

    def __eq__(self, other):
        return self.level == other.level and self.stock_id == other.stock_id and self.point.strftime(
            '%Y-%m-%d %H:%M') == other.point.strftime('%Y-%m-%d %H:%M') and self.type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)

    class Meta:
        # db_table = 'cl_point_result'
        db_table = 'cl_ptest'
