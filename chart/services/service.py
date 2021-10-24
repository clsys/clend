from chart.models import *


class Service:
    def create_new_gain(self, userid, stock_id, trade_type):
        gain = Gain()
        query = Gain.objects.filter(userid=userid)
        if query:
            return False
        gain.userid = userid + "." + stock_id
        gain.trade_type = trade_type
        gain.stock_id = stock_id
        gain.origin_funds = 10000000
        gain.origin_position = 1000
        gain.today_position = 0
        gain.save()
        return True

    def query(self):
        return Gain.objects.all()

    def get_trade_by_query(self):
        return Gain.objects.all()
