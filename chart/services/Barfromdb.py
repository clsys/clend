from django.db import connection
from chart.objects import RawBar
from chart.constant import freq_map


class BarFromDb:
    def get_latest_1m_bar(self, freq, symbol):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM 600809_XSHG_{freq} order by Date desc limit 0,1")
            res = cursor.fetchone()
            return RawBar(symbol=symbol, dt=res[0], id=0, freq=freq_map[freq],
                          open=round(float(res[1]), 2),
                          close=round(float(res[2]), 2),
                          high=round(res[3], 2),
                          low=round(res[4], 2),
                          vol=int(res[5]))

    def get(self, freq, symbol):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM 600809_XSHG_{freq}")
            desc = cursor.description
            list = [
                dict(zip([col[0] for col in desc], row))
                for row in cursor.fetchall()
            ]
            ret = []
            id = 0
            for k in list:
                id += 1
                ret.append(RawBar(symbol=symbol, dt=k['Date'], id=id, freq=freq_map[freq],
                                  open=round(float(k['Open']), 2),
                                  close=round(float(k['Close']), 2),
                                  high=round(k['High'], 2),
                                  low=round(k['Low'], 2),
                                  vol=int(k['Volume'])))
            return ret
