from jqdatasdk import *
from clend.settings import SETTINGS

auth(SETTINGS["jq.username"], SETTINGS["jq.password"])  # 账号是申请时所填写的手机号；密码为聚宽官网登录密码，新申请用户默认为手机号后6位
print(get_query_count())
# df = get_bars('000001.XSHE', 5, unit='120m',fields=['date','open','close','high','low','volume','money'],include_now=False,end_dt='2018-12-05')
# http和api每次最多获取5000数据
# 每次获取20天数据，20*240=4800
# 每次获取50次20天数据
if __name__ == '__main__':
    pass