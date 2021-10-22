from chart.models import *


class Service:
    def create_new_gain(self, userid, stock_id, trade_type):
        gain = Gain()
        query = Gain.objects.filter(userid=userid)
        if query:
            return False
        gain.userid = userid
        gain.trade_type = trade_type
        gain.stock_id = stock_id
        gain.cur_funds = 10000000
        gain.origin_funds = 0
        gain.cur_position = 0
        gain.origin_position = 0
        gain.save()
        return True

    def query(self):
        return Gain.objects.all()

    def get_trade_by_query(self):
        return Gain.objects.all()