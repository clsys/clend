from trade.gateways.xtp.xtp_gateway import XtpGateway
from typing import Any, Dict, List
from time import sleep
from trade.event import EventEngine
from trade.constant import Exchange
from trade.object import SubscribeRequest

default_setting: Dict[str, Any] = {
    "账号": "53191002369",
    "密码": "p2ThwvmE",
    "客户号": 1,
    "行情地址": "119.3.103.38",
    "行情端口": 6002,
    "交易地址": "122.112.139.0",
    "交易端口": 6101,
    "行情协议": "TCP",
    "日志级别": "FATAL",
    "授权码": "b8aa7173bba3470e390d787219b2112e"
}

xtp = XtpGateway(EventEngine())
xtp.connect(default_setting)
sleep(3)
sse_reqs = ['600519', '600809', '600008', '600009']
szse_reqs = ['']
sub_sse_reqs = []
sub_szse_reqs = []
for i in sse_reqs:
    if len(i) == 6:
        sub_sse_reqs.append(SubscribeRequest(i, Exchange.SSE))
for i in szse_reqs:
    if len(i) == 6:
        sub_szse_reqs.append(SubscribeRequest(i, Exchange.SZSE))
# req1 = SubscribeRequest('600519', Exchange.SSE)
# req2 = SubscribeRequest('600809', Exchange.SSE)
# req3 = SubscribeRequest('600008', Exchange.SSE)
# req4 = SubscribeRequest('600009', Exchange.SSE)
# xtp.subscribe(req1)
# xtp.subscribe(req2)
# xtp.subscribe(req3)
# xtp.subscribe(req4)

if __name__ == '__main__':
    while True:
        sleep(1)
        for i in sub_sse_reqs:
            xtp.subscribe(i)
        # xtp.subscribe(req2)
        # xtp.subscribe(req3)
        # xtp.subscribe(req4)
        print('=====================')
