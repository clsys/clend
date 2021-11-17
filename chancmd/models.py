# coding=utf-8
# 无用了，sqlalchemy无法解决问题，对于单表来说是很好用的
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime, Numeric, SMALLINT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()

Base = declarative_base()
engine = create_engine('mysql://root:@82.156.27.141/vnpy?charset=utf8&password=rooT@123', echo=True)


def make_bar(Base, table_name):
    class BarData(Base):
        # bar_600809_{1m,5m,30m,1d}
        __tablename__ = table_name

        __table_args__ = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
            'extend_existing': True
        }

        # id = Column(Integer, primary_key=True)
        # symbol = Column(String(255))
        # exchange = Column(String(255))
        datetime = Column(DateTime, index=True, unique=True)
        # interval = Column(String(255))
        volume = Column(Integer)
        open_interest = Column(Numeric(10, 2))
        open_price = Column(Numeric(10, 2))
        high_price = Column(Numeric(10, 2))
        low_price = Column(Numeric(10, 2))
        close_price = Column(Numeric(10, 2))

    return BarData


tick_class_dict = {}


class TickClass(Base):
    __abstract__ = True
    # __tablename__ should be 'ad_stat_%s'
    datetime = Column(DateTime, primary_key=True)
    # name = Column(String(255))
    volume = Column(Integer)
    open_interest = Column(Numeric(10, 2))
    last_price = Column(Numeric(10, 2))
    last_volume = Column(Integer)
    limit_up = Column(Numeric(10, 2))
    limit_down = Column(Numeric(10, 2))

    open_price = Column(Numeric(10, 2))
    high_price = Column(Numeric(10, 2))
    low_price = Column(Numeric(10, 2))
    pre_close = Column(Numeric(10, 2))

    bid_price_1 = Column(Numeric(10, 2))
    bid_price_2 = Column(Numeric(10, 2))
    bid_price_3 = Column(Numeric(10, 2))
    bid_price_4 = Column(Numeric(10, 2))
    bid_price_5 = Column(Numeric(10, 2))

    ask_price_1 = Column(Numeric(10, 2))
    ask_price_2 = Column(Numeric(10, 2))
    ask_price_3 = Column(Numeric(10, 2))
    ask_price_4 = Column(Numeric(10, 2))
    ask_price_5 = Column(Numeric(10, 2))

    bid_volume_1 = Column(Integer)
    bid_volume_2 = Column(Integer)
    bid_volume_3 = Column(Integer)
    bid_volume_4 = Column(Integer)
    bid_volume_5 = Column(Integer)

    ask_volume_1 = Column(Integer)
    ask_volume_2 = Column(Integer)
    ask_volume_3 = Column(Integer)
    ask_volume_4 = Column(Integer)
    ask_volume_5 = Column(Integer)


def get_symbol_tick_model(symbol):
    def get_class_name_and_table_name(symbol):
        return f'TickClass{symbol}', f'tick_{symbol}'

    if symbol not in tick_class_dict:
        cls_name, table_name = get_class_name_and_table_name(symbol)
        cls = type(cls_name, (TickClass,), {'__tablename__': table_name})
        tick_class_dict[symbol] = cls
    return tick_class_dict[symbol]


def make_tick(Base, table_name):
    class TickData(Base):
        __tablename__ = table_name
        __table_args__ = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
            'extend_existing': True
        }
        # id = Column(Integer, primary_key=True)
        # symbol = Column(String(255))
        # exchange = Column(String(255))
        datetime = Column(DateTime, primary_key=True)
        # name = Column(String(255))
        volume = Column(Integer)
        open_interest = Column(Numeric(10, 2))
        last_price = Column(Numeric(10, 2))
        last_volume = Column(Integer)
        limit_up = Column(Numeric(10, 2))
        limit_down = Column(Numeric(10, 2))

        open_price = Column(Numeric(10, 2))
        high_price = Column(Numeric(10, 2))
        low_price = Column(Numeric(10, 2))
        pre_close = Column(Numeric(10, 2))

        bid_price_1 = Column(Numeric(10, 2))
        bid_price_2 = Column(Numeric(10, 2))
        bid_price_3 = Column(Numeric(10, 2))
        bid_price_4 = Column(Numeric(10, 2))
        bid_price_5 = Column(Numeric(10, 2))

        ask_price_1 = Column(Numeric(10, 2))
        ask_price_2 = Column(Numeric(10, 2))
        ask_price_3 = Column(Numeric(10, 2))
        ask_price_4 = Column(Numeric(10, 2))
        ask_price_5 = Column(Numeric(10, 2))

        bid_volume_1 = Column(Integer)
        bid_volume_2 = Column(Integer)
        bid_volume_3 = Column(Integer)
        bid_volume_4 = Column(Integer)
        bid_volume_5 = Column(Integer)

        ask_volume_1 = Column(Integer)
        ask_volume_2 = Column(Integer)
        ask_volume_3 = Column(Integer)
        ask_volume_4 = Column(Integer)
        ask_volume_5 = Column(Integer)

    return TickData


def get_session():
    Session = sessionmaker(bind=engine)
    return Session()


def create_bar_table(symbol, interval):
    make_bar(Base, f'bar_{symbol}_{interval}')
    Base.metadata.create_all(engine)


def create_tick_table(symbol, interval):
    tick_data = make_tick(Base, f'tick_{symbol}_{interval}')
    Base.metadata.create_all(engine)
    return tick_data


# 定义User对象:
class User(Base):
    # 表的名字:
    __tablename__ = 'user'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    age = Column(Integer)
    deleted = Column(Integer)

    def __str__(self):
        return "id: {}, name: {}, age: {}, deleted: {}" \
            .format(self.id, self.name, self.age, self.deleted)


class Point(Base):
    # 表的名字:
    __tablename__ = 'cl_point'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    stock_id = Column(String(20))
    level = Column(String(10))
    point = Column(DateTime)
    type = Column(String(2))
    evaluation_time = Column(DateTime)
    valid = Column(SMALLINT)
    invalid_time = Column(DateTime)
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
