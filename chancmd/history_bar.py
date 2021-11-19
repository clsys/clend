from jqdatasdk import *
from chancmd.models import *
from trade.object import TickData
import warnings
from sqlalchemy import exc as sa_exc
from clend.settings import SETTINGS

auth(SETTINGS["jq.username"], SETTINGS["jq.password"])  # 账号是申请时所填写的手机号；密码为聚宽官网登录密码，新申请用户默认为手机号后6位

print(get_query_count())

# 只保存1分钟数据
end_dt = '2021-11-11'
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=sa_exc.SAWarning)
    # code here...


# 更新所有的股票列表
def all_securites():
    pass


# 手动更新，每次更新时间特别长
def history_task():
    # http和api每次最多获取5000数据
    # 每次获取20天数据，20*240=4800
    # 每次获取50次20天数据
    df = get_bars('000001.XSHE', 4800, unit='1m', fields=['date', 'open', 'close', 'high', 'low', 'volume', 'money'],
                  include_now=False, end_dt=end_dt)


# 4565支股票，每天增量更新，检查数据错误和check leak data
# 每天结束的时候更新，4565*240
def real_task():
    pass


tick_map = {}

if __name__ == '__main__':
    tick_table = create_tick_table('0000000', '1m')
    new_tick = tick_table(datetime='2021-09-09')
    session = get_session()
    session.add(new_tick)
    session.commit()
    session.close()


def save_tick2(tick: TickData):
    global tick_map
    if tick.symbol not in tick_map.keys():
        tick_table = create_tick_table(tick.symbol, '1m')
        tick_map[tick.symbol] = tick_table
    tick_table = get_symbol_tick_model(tick.symbol)
    new_tick = tick_table(datetime=tick.datetime,
                          volume=tick.volume,
                          last_price=tick.last_price,
                          limit_up=tick.limit_up,
                          limit_down=tick.limit_down,
                          open_price=tick.open_price,
                          high_price=tick.high_price,
                          low_price=tick.low_price,
                          pre_close=tick.pre_close
                          )
    session.add(new_tick)
    session.commit()


def save_tick(tick: TickData):
    global tick_map
    tick_table = None
    if tick.symbol in tick_map.keys():
        tick_table = tick_map[tick.symbol]
        print(type(tick_table))
        print(tick_table)
    else:
        tick_table = create_tick_table(tick.symbol, '1m')
        tick_map[tick.symbol] = tick_table
    if tick_table:
        new_tick = tick_table(datetime=tick.datetime,
                              volume=tick.volume,
                              last_price=tick.last_price,
                              limit_up=tick.limit_up,
                              limit_down=tick.limit_down,
                              open_price=tick.open_price,
                              high_price=tick.high_price,
                              low_price=tick.low_price,
                              pre_close=tick.pre_close
                              )
        session = get_session()
        session.add(new_tick)
        session.commit()
        session.close()
    else:
        print('None')


if __name__ == '__main__':
    pass
