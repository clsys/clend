from django.test import TestCase

# Create your tests here.
from settings import SETTINGS
from chanlun.hsdata import Data
import pandas as pd
from chart.kline import get_kline
from chart.utils.tools import raw_data_to_array
from chart.chanlun import calculate_bs
from datetime import datetime

def main():
    data = Data()
    bars = get_kline(symbol='600519.SH', freq='1m', count=20)
    klist = raw_data_to_array(bars)
    print(klist[0])
    print(len(klist))
    startList = klist[0:1000]
    for i in range(100, len(klist)):
        startList.append(klist[i])
        strokesList, lineList, pivotList, buy_list, sell_list, buy_list_history, sell_list_history = calculate_bs(
            startList)
        print('##############buy_list###############' + str(klist[i][0]))
        print(buy_list)
        print('##############sell_list###############' + str(klist[i][0]))
        print(sell_list)
        print('##############pivotList###############' + str(klist[i][0]))
        print(pivotList)

if __name__ == '__main__':
    main()
    # savedb()
