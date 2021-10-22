from turtle import pd
from chanlun.hsdata import Data
from chart.objects import RawBar
from chart.constant import freq_map
from datetime import datetime

data = Data()


def get_kline(symbol, end_date=datetime.now(), freq='1m', count=2000):
    rows = data.get_bars(symbol, 20, end_date.strftime('%Y-%m-%d'), freq)
    bars = []
    i = 0
    for row in rows:
        order = ['date', 'time', 'open', 'close', 'high', 'low', 'turnover_volume']

        # row = ['date', 'open', 'close', 'high', 'low', 'volume', 'money']
        h = str(row[1])[:-2]
        m = str(row[1])[-2:]
        dt = datetime.strptime(row[0] + " " + h + ":" + m + ":" + "00", "%Y-%m-%d %H:%M:%S")
        i += 1
        bars.append(RawBar(symbol=symbol, dt=dt, id=i, freq=freq_map[freq],
                           open=round(float(row[2]), 2),
                           close=round(float(row[3]), 2),
                           high=round(float(row[4]), 2),
                           low=round(float(row[5]), 2),
                           vol=int(row[6])))
    return bars
