# coding: utf-8
from dataclasses import dataclass
from datetime import datetime
from typing import List
from transitions import Machine

from chart.constant import Mark, Direction, Freq, Operate


@dataclass
class Tick:
    symbol: str
    name: str = ""
    price: float = 0
    vol: float = 0


@dataclass
class RawBar:
    """原始K线元素"""
    symbol: str
    id: int  # id 必须是升序
    dt: datetime
    freq: Freq
    open: [float, int]
    close: [float, int]
    high: [float, int]
    low: [float, int]
    vol: [float, int]
    amount: [float, int] = None


@dataclass
class NewBar:
    """去除包含关系后的K线元素"""
    symbol: str
    id: int  # id 必须是升序
    dt: datetime
    freq: Freq
    open: [float, int]
    close: [float, int]
    high: [float, int]
    low: [float, int]
    vol: [float, int]
    amount: [float, int] = None
    elements: List = None  # 存入具有包含关系的原始K线


@dataclass
class FX:
    symbol: str
    dt: datetime
    mark: Mark
    high: [float, int]
    low: [float, int]
    fx: [float, int]
    power: str = None
    elements: List = None


@dataclass
class FakeBI:
    """虚拟笔：主要为笔的内部分析提供便利"""
    symbol: str
    sdt: datetime
    edt: datetime
    direction: Direction
    high: [float, int]
    low: [float, int]
    power: [float, int]


@dataclass
class BI:
    symbol: str
    fx_a: FX = None  # 笔开始的分型
    fx_b: FX = None  # 笔结束的分型
    fxs: List = None  # 笔内部的分型列表
    direction: Direction = None
    high: float = None
    low: float = None
    power: float = None
    bars: List = None
    rsq: float = None
    change: float = None
    length: float = None
    fake_bis: List = None

    def __post_init__(self):
        self.sdt = self.fx_a.dt
        self.edt = self.fx_b.dt


@dataclass
class Signal:
    signal: str = None

    # score 取值在 0~100 之间，得分越高，信号越强
    score: int = 0

    # k1, k2, k3 是信号名称
    k1: str = "任意"
    k2: str = "任意"
    k3: str = "任意"

    # v1, v2, v3 是信号取值
    v1: str = "任意"
    v2: str = "任意"
    v3: str = "任意"

    # 任意 出现在模板信号中可以指代任何值

    def __post_init__(self):
        if not self.signal:
            self.signal = f"{self.k1}_{self.k2}_{self.k3}_{self.v1}_{self.v2}_{self.v3}_{self.score}"
        else:
            self.k1, self.k2, self.k3, self.v1, self.v2, self.v3, score = self.signal.split("_")
            self.score = int(score)

        if self.score > 100 or self.score < 0:
            raise ValueError("score 必须在0~100之间")

    def __repr__(self):
        return f"Signal('{self.signal}')"

    @property
    def key(self) -> str:
        """获取信号名称"""
        key = ""
        for k in [self.k1, self.k2, self.k3]:
            if k != "任意":
                key += k + "_"
        return key.strip("_")

    @property
    def value(self) -> str:
        """获取信号值"""
        return f"{self.v1}_{self.v2}_{self.v3}_{self.score}"

    def is_match(self, s: dict) -> bool:
        """判断信号是否与信号列表中的值匹配

        :param s: 所有信号字典
        :return: bool
        """
        key = self.key
        v = s.get(key, None)
        if not v:
            raise ValueError(f"{key} 不在信号列表中")

        v1, v2, v3, score = v.split("_")
        if int(score) >= self.score:
            if v1 == self.v1 or self.v1 == '任意':
                if v2 == self.v2 or self.v2 == '任意':
                    if v3 == self.v3 or self.v3 == '任意':
                        return True
        return False


@dataclass
class Factor:
    name: str
    # signals_all 必须全部满足的信号
    signals_all: List[Signal]
    # signals_any 满足其中任一信号，允许为空
    signals_any: List[Signal] = None

    def is_match(self, s: dict) -> bool:
        """判断 factor 是否满足"""
        for signal in self.signals_all:
            if not signal.is_match(s):
                return False

        if not self.signals_any:
            return True

        for signal in self.signals_any:
            if signal.is_match(s):
                return True
        return False


@dataclass
class Event:
    name: str
    operate: Operate

    # 多个信号组成一个因子，多个因子组成一个事件。
    # 单个事件是一系列同类型因子的集合，事件中的任一因子满足，则事件为真。
    factors: List[Factor]

    def is_match(self, s: dict):
        """判断 event 是否满足"""
        for factor in self.factors:
            if factor.is_match(s):
                # 顺序遍历，找到第一个满足的因子就退出。建议因子列表按关注度从高到低排序
                return True, factor.name

        return False, None


class Position:
    def __init__(self, symbol: str,
                 hold_long_a: float = 0.5,
                 hold_long_b: float = 0.8,
                 hold_long_c: float = 1.0,
                 hold_short_a: float = -0.5,
                 hold_short_b: float = -0.8,
                 hold_short_c: float = -1.0,
                 ):
        """持仓对象

        :param symbol: 标的代码
        :param hold_long_a: 首次开多仓后的仓位
        :param hold_long_b: 第一次加多后的仓位
        :param hold_long_c: 第二次加多后的仓位
        :param hold_short_a: 首次开空仓后的仓位
        :param hold_short_b: 第一次加空后的仓位
        :param hold_short_c: 第二次加空后的仓位
        """
        self.symbol = symbol
        self.pos_map = {
            "hold_long_a": hold_long_a, "hold_long_b": hold_long_b, "hold_long_c": hold_long_c, "hold_money": 0,
            "hold_short_a": hold_short_a,  "hold_short_b": hold_short_b,  "hold_short_c": hold_short_c
        }
        self.states = list(self.pos_map.keys())
        self.machine = Machine(model=self, states=self.states, initial='hold_money')
        self.machine.add_transition('long_open', 'hold_money', 'hold_long_a')
        self.machine.add_transition('long_add1', 'hold_long_a', 'hold_long_b')
        self.machine.add_transition('long_add2', 'hold_long_b', 'hold_long_c')
        self.machine.add_transition('long_reduce1', 'hold_long_c', 'hold_long_b')
        self.machine.add_transition('long_reduce2', 'hold_long_b', 'hold_long_a')
        self.machine.add_transition('long_exit', ['hold_long_a', 'hold_long_b', 'hold_long_c'], 'hold_money')

        self.machine.add_transition('short_open', 'hold_money', 'hold_short_a')
        self.machine.add_transition('short_add1', 'hold_short_a', 'hold_short_b')
        self.machine.add_transition('short_add2', 'hold_short_b', 'hold_short_c')
        self.machine.add_transition('short_reduce1', 'hold_short_c', 'hold_short_b')
        self.machine.add_transition('short_reduce2', 'hold_short_b', 'hold_short_a')
        self.machine.add_transition('short_exit', ['hold_short_a', 'hold_short_b', 'hold_short_c'], 'hold_money')

    @property
    def pos(self):
        return self.pos_map[self.state]

