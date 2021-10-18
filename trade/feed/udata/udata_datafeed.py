from datetime import datetime, timedelta
from typing import List, Optional
from pytz import timezone

from hs_udata import set_token
from hs_udata.apis.stock.api import fut_quote_minute, stock_quote_minutes
from pandas import DataFrame

from clend.settings import SETTINGS
from trade.constant import Exchange, Interval
from trade.object import BarData, HistoryRequest
from trade.datafeed import BaseDatafeed

EXCHANGE_VT2UDATA = {
    Exchange.CFFEX.value: "CFE",
    Exchange.SHFE.value: "SHF",
    Exchange.DCE.value: "DCE",
    Exchange.CZCE.value: "CZC",
    Exchange.INE.value: "INE",
    Exchange.SSE.value: "SH",
    Exchange.SZSE.value: "SZ"
}

INTERVAL_VT2RQ = {
    Interval.MINUTE.value: "1m",
    Interval.HOUR.value: "60m",
    Interval.DAILY.value: "1d",
}

INTERVAL_ADJUSTMENT_MAP = {
    Interval.MINUTE.value: timedelta(minutes=1),
    Interval.HOUR.value: timedelta(hours=1),
    Interval.DAILY.value: timedelta()  # no need to adjust for daily bar
}

CHINA_TZ = timezone("Asia/Shanghai")


def convert_symbol(symbol: str, exchange: Exchange) -> str:
    """将交易所代码转换为UData代码"""
    exchange_str = EXCHANGE_VT2UDATA.get(exchange, "")
    return f"{symbol.upper()}.{exchange_str}"


class UdataDatafeed(BaseDatafeed):
    """恒生UData数据服务接口"""

    def __init__(self):
        """"""
        self.token: str = SETTINGS["datafeed.password"]

        self.inited: bool = False

    def init(self) -> bool:
        """初始化"""
        set_token(self.token)
        self.inited = True
        return True

    def query_bar_history(self, req: HistoryRequest) -> Optional[List[BarData]]:
        """查询K线数据"""
        if not self.inited:
            self.init()

        # 只支持分钟线
        if req.interval.value != Interval.MINUTE.value:
            return None

        # 期货
        if req.exchange.value in {
            Exchange.CFFEX.value,
            Exchange.SHFE.value,
            Exchange.CZCE.value,
            Exchange.DCE.value,
            Exchange.INE.value
        }:
            return self.query_futures_bar_history(req)
        # 股票
        elif req.exchange.value in {
            Exchange.SSE.value,
            Exchange.SZSE.value
        }:
            return self.query_equity_bar_history(req)
        # 其他
        else:
            return None

    def query_futures_bar_history(self, req: HistoryRequest) -> Optional[List[BarData]]:
        """查询期货分钟K线数据"""
        symbol = req.symbol
        exchange = req.exchange
        interval = req.interval
        start = req.start
        end = req.end

        udata_symbol = convert_symbol(symbol, exchange.value)
        adjustment = timedelta(minutes=1)

        df: DataFrame = fut_quote_minute(
            en_prod_code=udata_symbol,
            begin_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d")
        )

        data: List[BarData] = []

        if len(df):
            for _, row in df.iterrows():
                timestr = f"{row.date} {str(row.time).rjust(4, '0')}"
                dt = datetime.strptime(timestr, "%Y-%m-%d %H%M") - adjustment
                dt = CHINA_TZ.localize(dt)

                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=dt,
                    open_price=row.open,
                    high_price=row.high,
                    low_price=row.low,
                    close_price=row.close,
                    volume=row.turnover_volume,
                    turnover=row.turnover_value,
                    open_interest=row.amount,
                    gateway_name="UDATA"
                )

                data.append(bar)

        return data

    def query_equity_bar_history(self, req: HistoryRequest) -> Optional[List[BarData]]:
        """查询股票分钟K线数据"""
        symbol = req.symbol
        exchange = req.exchange
        interval = req.interval
        start = req.start
        end = req.end

        udata_symbol = convert_symbol(symbol, exchange)
        adjustment = timedelta(minutes=1)

        df: DataFrame = stock_quote_minutes(
            en_prod_code=udata_symbol,
            begin_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d")
        )

        data: List[BarData] = []

        if len(df):
            for _, row in df.iterrows():
                timestr = f"{row.date} {str(row.time).rjust(4, '0')}"
                dt = datetime.strptime(timestr, "%Y-%m-%d %H%M") - adjustment
                dt = CHINA_TZ.localize(dt)

                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=dt,
                    open_price=row.open,
                    high_price=row.high,
                    low_price=row.low,
                    close_price=row.close,
                    volume=row.turnover_volume,
                    turnover=row.turnover_value,
                    gateway_name="UDATA"
                )

                data.append(bar)

        return data
