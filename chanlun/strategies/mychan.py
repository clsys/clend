from datetime import datetime
from typing import Any

from trade.utility import BarGenerator, ArrayManager
from trade.object import OrderData, TradeData, BarData, TickData, StopOrder
from trade.template import Template
from copy import copy
import numpy as np
from chart.utils.ta import SMA, MACD


class JChan(Template):
    author = "jc"

    parameters = ["period", "stroke_type", "pivot_type", "buy1", "buy2", "buy3", "sell1", "sell2", "sell3",
                  "dynamic_reduce"]
    variables = ["stroke_list", "line_list", "pivot_list", "trend_list", "buy_list", "sell_list"]

    def __init__(self, engine, strategy_name, vt_symbol, setting, include=True, build_pivot=False):
        """"""
        super().__init__(engine, strategy_name, vt_symbol, setting)
        self.k_list = []
        self.chan_k_list = []
        self.fx_list = []
        self.stroke_list = []
        self.line_list = []
        self.line_index = {}
        self.line_feature = []
        self.s_feature = []
        self.x_feature = []

        self.pivot_list = []
        self.trend_list = []
        self.buy_list = []
        self.x_buy_list = []
        self.sell_list = []
        self.x_sell_list = []
        self.macd = {}
        # 头寸控制
        self.buy1 = 100
        self.buy2 = 200
        self.buy3 = 200
        self.sell1 = 100
        self.sell2 = 200
        self.sell3 = 200
        # 动力减弱最小指标
        self.dynamic_reduce = 0
        # 笔生成方法，new, old
        # 是否进行K线包含处理
        self.include = include
        # 中枢生成方法，stroke, line
        # 使用笔还是线段作为中枢的构成, true使用线段
        self.build_pivot = build_pivot

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("chan策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("chan策略启动")
        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("chan策略停止")

        self.put_event()

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        self.on_period(bar)

    def on_period(self, bar: BarData):
        self.k_list.append(bar)
        if self.include:
            self.on_process_k_include(bar)
        else:
            self.on_process_k_no_include(bar)

    def on_process_k_include(self, bar: BarData):
        """合并k线"""
        if len(self.chan_k_list) < 3:
            self.chan_k_list.append(bar)
        else:
            pre_bar = self.chan_k_list[-2]
            last_bar = self.chan_k_list[-1]
            if (last_bar.high >= bar.high and last_bar.low <= bar.low) or (
                    last_bar.high <= bar.high and last_bar.low >= bar.low):
                if last_bar.high > pre_bar.high:
                    new_bar = copy(bar)
                    new_bar.high = max(last_bar.high, new_bar.high)
                    new_bar.low = max(last_bar.low, new_bar.low)
                    # new_bar.open = max(last_bar.open, new_bar.open)
                    # new_bar.close = max(last_bar.close, new_bar.close)
                else:
                    new_bar = copy(bar)
                    new_bar.high = min(last_bar.high, new_bar.high)
                    new_bar.low = min(last_bar.low, new_bar.low)
                    # new_bar.open = min(last_bar.open, new_bar.open)
                    # new_bar.close = min(last_bar.close, new_bar.close)

                self.chan_k_list[-1] = new_bar
                print("combine k line: " + str(new_bar.dt))
            else:
                self.chan_k_list.append(bar)
            # 包含和非包含处理的k线都需要判断是否分型了
            self.on_process_fx(self.chan_k_list)

    def on_process_k_no_include(self, bar: BarData):
        """不用合并k线"""
        self.chan_k_list.append(bar)
        self.on_process_fx(self.chan_k_list)

    def on_process_fx(self, data):
        if len(data) > 2:
            flag = False
            if data[-2].high > data[-1].high and data[-2].high > data[-3].high:
                # 形成顶分型 [high, low, dt, direction, index of chan_k_list]
                self.fx_list.append([data[-2].high, data[-2].low, data[-2].dt, 'up', len(data) - 2])
                flag = True

            if data[-2].low < data[-1].low and data[-2].low < data[-3].low:
                # 形成底分型
                self.fx_list.append([data[-2].high, data[-2].low, data[-2].dt, 'down', len(data) - 2])
                flag = True

            if flag:
                self.on_stroke(self.fx_list[-1])
                print("fx_list: ")
                print(self.fx_list[-1])

    def on_stroke(self, data):
        """生成笔"""
        if len(self.stroke_list) < 2:
            self.stroke_list.append(data)
        else:
            last_fx = self.stroke_list[-1]
            cur_fx = data
            # 分型之间需要超过三根chank线
            # 延申也是需要条件的
            if last_fx[3] == cur_fx[3]:
                if (last_fx[3] == 'down' and cur_fx[1] < last_fx[1]) or (
                        last_fx[3] == 'up' and cur_fx[0] > last_fx[0]):
                    # 笔延申
                    self.stroke_list[-1] = cur_fx
                    # 修正倒数第二个分型是否是最高的顶分型或者是否是最低的底分型
                    start = -2
                    stroke_change = None
                    if cur_fx[3] == 'down':
                        while len(self.fx_list) > abs(start) and self.fx_list[start][2] > last_fx[2]:
                            if self.fx_list[start][3] == 'up' and self.fx_list[start][0] > self.stroke_list[-2][0]:
                                stroke_change = self.fx_list[start]
                            start -= 1
                    else:
                        while len(self.fx_list) > abs(start) and self.fx_list[start][2] > last_fx[2]:
                            if self.fx_list[start][3] == 'down' and self.fx_list[start][1] < self.stroke_list[-2][1]:
                                stroke_change = self.fx_list[start]
                            start -= 1
                    if stroke_change:
                        print('stroke_change')
                        print(stroke_change)

                        # 更新中枢的信息
                        if self.pivot_list:
                            last_pivot = self.pivot_list[-1]
                            if self.stroke_list[-2][2] == last_pivot[4][3][2]:
                                last_pivot[1] = stroke_change[2]
                                if stroke_change[3] == 'up':
                                    ZG = min(self.stroke_list[-4][0], self.stroke_list[-2][0])
                                    last_pivot[3] = ZG
                                else:
                                    ZD = max(self.stroke_list[-4][0], self.stroke_list[-2][0])
                                    last_pivot[2] = ZD
                                print('pivot_change')
                                print(self.pivot_list[-1])

                        self.stroke_list[-2] = stroke_change
                        if len(self.stroke_list) > 2:
                            cur_fx = self.stroke_list[-2]
                            last_fx = self.stroke_list[-3]
                            self.macd[cur_fx[2]] = self.cal_macd(last_fx[2], cur_fx[2])

                        if cur_fx[4] - self.stroke_list[-2][4] < 4:
                            self.stroke_list.pop()

            else:
                if (cur_fx[4] - last_fx[4] > 3) and (
                        (cur_fx[3] == 'down' and cur_fx[1] < last_fx[1] and cur_fx[0] < last_fx[0]) or (
                        cur_fx[3] == 'up' and cur_fx[0] > last_fx[0] and cur_fx[1] > last_fx[1])):
                    # 笔新增
                    self.stroke_list.append(cur_fx)
                    print("stroke_list: ")
                    print(self.stroke_list[-1])
                    # print(self.stroke_list)

            if self.build_pivot:
                self.on_line(self.stroke_list)
            else:
                if len(self.stroke_list) > 1:
                    cur_fx = self.stroke_list[-1]
                    last_fx = self.stroke_list[-2]
                    self.macd[cur_fx[2]] = self.cal_macd(last_fx[2], cur_fx[2])
                self.on_line(self.stroke_list)
                self.on_pivot(self.stroke_list)

    def on_line(self, data):
        # line_list保持和stroke_list结构相同，都是由分型构成的
        # 特征序列则不同，
        if len(data) > 4:
            # print('line_index:')
            # print(self.line_index)
            if data[-1][3] == 'up' and data[-3][0] >= data[-1][0] and data[-3][0] >= data[-5][0]:
                if not self.line_list or self.line_list[-1][3] == 'down':
                    if not self.line_list or (len(self.stroke_list) - 3) - self.line_index[
                        str(self.line_list[-1][2])] > 2:
                        # 出现顶
                        self.line_list.append(data[-3])
                        self.line_index[str(self.line_list[-1][2])] = len(self.stroke_list) - 3
                else:
                    # 延申顶
                    if self.line_list[-1][0] < data[-3][0]:
                        self.line_list[-1] = data[-3]
                        self.line_index[str(self.line_list[-1][2])] = len(self.stroke_list) - 3
            if data[-1][3] == 'down' and data[-3][1] <= data[-1][1] and data[-3][1] <= data[-5][1]:
                if not self.line_list or self.line_list[-1][3] == 'up':
                    if not self.line_list or (len(self.stroke_list) - 3) - self.line_index[
                        str(self.line_list[-1][2])] > 2:
                        # 出现底
                        self.line_list.append(data[-3])
                        self.line_index[str(self.line_list[-1][2])] = len(self.stroke_list) - 3
                else:
                    # 延申底
                    if self.line_list[-1][1] > data[-3][1]:
                        self.line_list[-1] = data[-3]
                        self.line_index[str(self.line_list[-1][2])] = len(self.stroke_list) - 3
            if self.line_list and self.build_pivot:
                if len(self.line_list) > 1:
                    cur_fx = self.line_list[-1]
                    last_fx = self.line_list[-2]
                    self.macd[cur_fx[2]] = self.cal_macd(last_fx[2], cur_fx[2])
                print('line_list:')
                print(self.line_list[-1])
                self.on_pivot(self.line_list)

    # def on_line(self, data):
    #     """
    #     不管线段从向上的笔开始，还是从向下的笔开始，对于笔的序列可能的情况
    #     0,1,2,3,4,5,6,7,8,9
    #     down,up,down,up,down,up,down,up,down,up,down,up,down,up,down,up,down,up
    #     up,down,up,down,up,down,up,down,up,down,up,down,up,down,up,down,up,down
    #     从第一个开始，0,2,4,6,8,10 如果序列 0.h > 2.h > 4.h < 6.h 0 -> 5
    #     1,3,5,7,9
    #     """
    #     # 计算能否构成线段，一个普通的线段的终结，至少需要7个分型才能构成线段，缺口的情况至少需要10个分型
    #     if len(self.stroke_list) < 7:
    #         return
    #
    #     # 开始时，寻找线段开始的地方
    #     start = 0
    #     if self.line_list:
    #         start = self.line_list[-1].index + 1
    #     last_line = None
    #
    #     even_list = [self.stroke_list[i] for i in range(start, len(self.stroke_list), 2)]
    #     odd_list = [self.stroke_list[i] for i in range(start + 1, len(self.stroke_list), 2)]
    #     even_fx_list = []
    #     odd_fx_list = []
    #     # 第一次计算特征序列分型，找到同方向的分型就行了
    #     for i in range(3, len(even_list)):
    #         cur_fx = self.process_fx(even_list[start:i])
    #         if not even_fx_list:
    #             even_fx_list.append(cur_fx)
    #         else:
    #             last_fx = even_fx_list[-1]
    #             if last_fx and cur_fx:
    #                 if last_fx.direc == cur_fx.direc:
    #                     even_fx_list[-1] = cur_fx;
    #                 else:
    #                     # 分型变了
    #                     break
    #
    #     for i in range(3, len(odd_list)):
    #         cur_fx = self.process_fx(odd_list[start:i])
    #         if not odd_fx_list:
    #             odd_fx_list.append(cur_fx)
    #         else:
    #             last_fx = odd_fx_list[-1]
    #             if last_fx and cur_fx:
    #                 if last_fx.direc == cur_fx.direc:
    #                     odd_fx_list[-1] = cur_fx;
    #                 else:
    #                     # 分型变了
    #                     break
    #     # 没有分型信息
    #     if even_fx_list or odd_fx_list:
    #         return
    #
    #     # 底分型是向下，顶分型是向上
    #     if even_fx_list[0].direc == 'up' and odd_fx_list[0].direc == 'up':
    #         self.line_list(even_fx_list[0])
    #         self.on_pivot(cur_fx)
    #
    #     if even_fx_list[0].direc == 'down' and odd_fx_list[0].direc == 'down':
    #         self.line_list(odd_fx_list[0])

    # 从last_line开始寻找

    # def on_pivot1(self, data):
    #     # 中枢列表[[日期1，日期2，中枢低点，中枢高点]]
    #     if len(data) > 3:
    #         cur_fx = data[-1]
    #         # 构成新的中枢
    #         if not self.pivot_list or (self.pivot_list and data[-2][2] > self.pivot_list[-1][1]):
    #             cur_pivot = [data[-4][2], cur_fx[2]]
    #             if cur_fx[3] == 'down':
    #                 ZD = max(data[-3][1], data[-1][1])
    #                 ZG = min(data[-4][0], data[-2][0])
    #                 if ZG > ZD:
    #                     cur_pivot.append(ZD)
    #                     cur_pivot.append(ZG)
    #                     self.pivot_list.append(cur_pivot)
    #             else:
    #                 ZD = max(data[-4][1], data[-2][1])
    #                 ZG = min(data[-3][0], data[-1][0])
    #                 if ZG > ZD:
    #                     cur_pivot.append(ZD)
    #                     cur_pivot.append(ZG)
    #                     self.pivot_list.append(cur_pivot)
    #             print("pivot_list:")
    #             print(self.pivot_list)
    #         else:
    #             # 中枢的延申
    #             last_pivot = self.pivot_list[-1]
    #             if cur_fx[3] == 'down':
    #                 # if cur_fx[1] > last_pivot[2] and cur_fx[1] < last_pivot[3]:
    #                 #     last_pivot[2] = cur_fx[1]
    #                 #     last_pivot[1] = cur_fx[2]
    #                 if cur_fx[1] < last_pivot[2]:
    #                     last_pivot[1] = cur_fx[2]
    #             else:
    #                 # if cur_fx[0] < last_pivot[3] and cur_fx[0] > last_pivot[2]:
    #                 #     last_pivot[3] = cur_fx[0]
    #                 #     last_pivot[1] = cur_fx[2]
    #                 if cur_fx[0] > last_pivot[3]:
    #                     last_pivot[1] = cur_fx[2]

    def on_pivot(self, data):
        # 中枢列表[[日期1，日期2，中枢低点，中枢高点, []]]]
        # 日期1：中枢开始的时间
        # 日期2：中枢结束的时间，可能延申
        # []: 构成中枢分型列表
        if len(data) > 4:
            # 构成笔或者是线段的分型
            cur_fx = data[-1]
            last_fx = data[-2]
            new_pivot = None
            # 构成新的中枢
            # if not self.pivot_list or (self.pivot_list and data[-2][2] > self.pivot_list[-1][1]):
            if not self.pivot_list or (self.pivot_list and data[-4][2] > self.pivot_list[-1][1]):
                cur_pivot = [data[-4][2], cur_fx[2]]
                if cur_fx[3] == 'down' and data[-2][0] > data[-4][0] and data[-2][1] > data[-4][1]:
                    ZD = max(data[-3][1], data[-1][1])
                    ZG = min(data[-4][0], data[-2][0])
                    if ZG > ZD:
                        cur_pivot.append(ZD)
                        cur_pivot.append(ZG)
                        cur_pivot.append(data[-4:])
                        new_pivot = cur_pivot
                        self.pivot_list.append(cur_pivot)
                if cur_fx[3] == 'up' and data[-2][0] < data[-4][0] and data[-2][1] < data[-4][1]:
                    ZD = max(data[-4][1], data[-2][1])
                    ZG = min(data[-3][0], data[-1][0])
                    if ZG > ZD:
                        cur_pivot.append(ZD)
                        cur_pivot.append(ZG)
                        cur_pivot.append(data[-4:])
                        new_pivot = cur_pivot
                        self.pivot_list.append(cur_pivot)
                if len(cur_pivot) > 2:
                    print("pivot_list:")
                    print(cur_pivot)
            else:
                if data[-2][2] <= self.pivot_list[-1][1]:
                    # 中枢的延申
                    last_pivot = self.pivot_list[-1]
                    if cur_fx[3] == 'down':
                        # 对于中枢，只取前三段构成max，min，后边不会再改变
                        # 在前三段中枢的中间
                        if cur_fx[1] > last_pivot[2] and cur_fx[1] < last_pivot[3]:
                            # last_pivot[2] = cur_fx[1]
                            last_pivot[1] = cur_fx[2]
                        # 更低了
                        if cur_fx[1] < last_pivot[2]:
                            # 第三段的线段延申的更低了
                            if last_fx[2] == last_pivot[4][-2][2]:
                                last_pivot[2] = max(last_pivot[4][-3][1], cur_fx[1])
                            last_pivot[1] = cur_fx[2]
                    else:
                        if cur_fx[0] < last_pivot[3] and cur_fx[0] > last_pivot[2]:
                            # last_pivot[3] = cur_fx[0]
                            last_pivot[1] = cur_fx[2]
                        if cur_fx[0] > last_pivot[3]:
                            if last_fx[2] == last_pivot[4][-2][2]:
                                last_pivot[3] = min(last_pivot[4][-3][0], cur_fx[0])
                            last_pivot[1] = cur_fx[2]
            self.on_trend(new_pivot, data)

    def cal_macd(self, start, end):
        sum = 0
        if start >= end:
            return sum
        close = np.array([x.close for x in self.chan_k_list if x.dt >= start and x.dt <= end], dtype=np.double)
        diff, dea, macd = MACD(close)
        for i, v in enumerate(macd.tolist()):
            sum += round(v, 4)
        return round(sum, 4)

    def on_trend(self, new_pivot, data):
        # 走势列表[[日期1，日期2，走势类型，[背驰点], [中枢]]]
        if new_pivot:
            data_list = new_pivot[4]
            if len(self.trend_list) > 0:
                last_pivot = self.pivot_list[-2]
                last_trend = self.trend_list[-1]
                # 上升趋势
                if new_pivot[2] > last_pivot[3]:
                    if last_trend[2] == 'up':
                        # 新的中枢继续延申趋势
                        last_trend[1] = new_pivot[1]
                        last_trend[4].append(new_pivot)
                        if data_list[0][3] == 'up' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] > 0:
                            # up->up，背驰情况下，下一步可能趋势反转，产生S1, 后续产生S2, S3
                            # 买点列表[[日期，值，类型, evaluation_time, valid, invalid_time]]
                            self.on_buy_sell([data_list[2][2], data_list[2][0], 'S1', self.k_list[-1].dt], True)
                        if data_list[0][3] == 'up' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] <= 0:
                            # up->up，能够形成B2, B3
                            self.on_buy_sell([data_list[1][2], data_list[1][1], 'B2', self.k_list[-1].dt], True)
                        # if data_list[0][3] == 'down' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] <= 0:
                        #     # up->up，能够形成B2, B3
                        #     self.on_buy_sell([data_list[2][2], data_list[2][1], 'B2', datetime.now()], True)
                    else:
                        # 形成了新的逆向趋势
                        self.trend_list.append([last_pivot[0], new_pivot[1], 'up', [], [last_pivot, new_pivot]])
                        # down->up,能够形成B2,B3
                        if data_list[0][3] == 'up' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] <= 0:
                            self.on_buy_sell([data_list[1][2], data_list[1][1], 'B2', self.k_list[-1].dt], True)
                        # if data_list[0][3] == 'down' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] <= 0:
                        #     self.on_buy_sell([data_list[2][2], data_list[2][1], 'B2', datetime.now()], True)
                # 下降趋势
                elif new_pivot[3] < last_pivot[2]:
                    if last_trend[2] == 'down':
                        last_trend[1] = new_pivot[1]
                        last_trend[4].append(new_pivot)

                        if data_list[0][3] == 'down' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] > 0:
                            # down->down，背驰情况下，下一步可能趋势反转，产生B1, 后续产生B2, B3
                            # 买点列表[[日期，值，类型, evaluation_time, valid, invalid_time]]
                            self.on_buy_sell([data_list[2][2], data_list[2][1], 'B1', self.k_list[-1].dt], True)

                        if data_list[0][3] == 'down' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] <= 0:
                            # down->down，能够形成S2, S3
                            self.on_buy_sell([data_list[1][2], data_list[1][0], 'S2', self.k_list[-1].dt], True)
                        # if data_list[0][3] == 'up' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] <= 0:
                        #     # down->down，能够形成S2, S3
                        #     self.on_buy_sell([data_list[2][2], data_list[2][0], 'S2', datetime.now()], True)
                    else:
                        # 形成了新的逆向趋势
                        self.trend_list.append([last_pivot[0], new_pivot[1], 'down', [], [last_pivot, new_pivot]])
                        # up->down 能够形成S2, S3
                        # if data_list[0][3] == 'up' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] <= 0:
                        #     self.on_buy_sell([data_list[2][2], data_list[2][0], 'S2', datetime.now()], True)
                        if data_list[0][3] == 'down' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] <= 0:
                            self.on_buy_sell([data_list[1][2], data_list[1][0], 'S2', self.k_list[-1].dt], True)

                # 盘整
                else:
                    self.trend_list.append([new_pivot[0], new_pivot[1], 'pz', [], [new_pivot]])
                    if last_trend[2] == 'up':
                        # 形成卖点，S1
                        if data_list[0][3] == 'up' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] > 0:
                            # 买点列表[[日期，值，类型, evaluation_time, valid, invalid_time]]
                            self.on_buy_sell([data_list[2][2], data_list[2][0], 'S1', self.k_list[-1].dt], True)
                    elif last_trend[2] == 'down':
                        # 形成买点，B1
                        if data_list[0][3] == 'down' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] > 0:
                            # 买点列表[[日期，值，类型, evaluation_time, valid, invalid_time]]
                            self.on_buy_sell([data_list[2][2], data_list[2][1], 'B1', self.k_list[-1].dt], True)
                    else:
                        # 前面仍然是盘整， 这种情况应该不存在
                        pass
            else:
                # 第一次盘整的情况
                self.trend_list.append([new_pivot[0], new_pivot[1], 'pz', [], [new_pivot]])
                if data_list[0][3] == 'up' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] > 0:
                    # 买点列表[[日期，值，类型, evaluation_time, valid, invalid_time]]
                    self.on_buy_sell([data_list[2][2], data_list[2][0], 'S1', self.k_list[-1].dt], True)
                if data_list[0][3] == 'down' and self.macd[data_list[0][2]] - self.macd[data_list[2][2]] > 0:
                    # 买点列表[[日期，值，类型, evaluation_time, valid, invalid_time]]
                    self.on_buy_sell([data_list[2][2], data_list[2][1], 'B1', self.k_list[-1].dt], True)

            # print('trend_list')
            # print(self.trend_list)
        else:
            if len(self.trend_list) > 0:
                # 如果中枢延续趋势跟随中枢延续
                cur_trend = self.trend_list[-1]
                cur_pivot = self.pivot_list[-1]
                if cur_pivot[1] > cur_trend[1] and cur_pivot[0] == cur_trend[0]:
                    cur_trend[1] = cur_pivot[1]

                cur_fx = self.fx_list[-1]
                # # 在有趋势的情况下判断背驰，没有新增的中枢
                # if cur_trend[2] == 'up' and cur_fx[3] == 'up' and cur_fx[2] in self.macd.keys() and cur_pivot[
                #     0] in self.macd.keys():
                #     if self.macd[cur_fx[2]] - self.macd[cur_pivot[0]] < 0:
                #         cur_trend[3].append(cur_fx[2])
                #
                # if cur_trend[2] == 'down' and cur_fx == 'down' and cur_fx[2] in self.macd.keys() and cur_pivot[
                #     0] in self.macd.keys():
                #     if self.macd[cur_fx[2]] - self.macd[cur_pivot[0]] > 0:
                #         cur_trend[3].append(cur_fx[2])

                if cur_trend[2] == 'pz':
                    pass

    def on_buy_sell(self, data, valid=True):
        if not data:
            return
        # 买点列表[[日期，值，类型, evaluation_time, valid, invalid_time]]
        # 卖点列表[[日期，值，类型, evaluation_time, valid, invalid_time]]
        if valid:
            if data[2].startswith('B'):
                print('buy:')
                print(data)
                self.buy_list.append(data)
            else:
                print('sell:')
                print(data)
                self.sell_list.append(data)
        else:
            if data[2].startswith('B'):
                print('buy:')
                print(data)
                self.x_buy_list.append(data)
            else:
                print('sell:')
                print(data)
                self.x_sell_list.append(data)

    def on_order(self, order: OrderData):
        pass

    def on_trade(self, trade: TradeData):
        pass

    def on_stop_order(self, stop_order: StopOrder):
        pass
