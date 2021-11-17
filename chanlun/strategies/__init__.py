from datetime import datetime


def cal_count_k(self, start: datetime, end: datetime, freq: str):
    global freq_count
    d1 = start
    d2 = end
    d1_sw_start = datetime.strptime(str(datetime.date(d1)) + ' 9:30', '%Y-%m-%d %H:%M')
    d1_sw_end = datetime.strptime(str(datetime.date(d1)) + ' 11:30', '%Y-%m-%d %H:%M')
    d1_xw_start = datetime.strptime(str(datetime.date(d1)) + ' 13:00', '%Y-%m-%d %H:%M')
    d1_xw_end = datetime.strptime(str(datetime.date(d1)) + ' 15:00', '%Y-%m-%d %H:%M')
    d2_sw_start = datetime.strptime(str(datetime.date(d2)) + ' 9:30', '%Y-%m-%d %H:%M')
    d2_sw_end = datetime.strptime(str(datetime.date(d2)) + ' 11:30', '%Y-%m-%d %H:%M')
    d2_xw_start = datetime.strptime(str(datetime.date(d2)) + ' 13:00', '%Y-%m-%d %H:%M')
    d2_xw_end = datetime.strptime(str(datetime.date(d2)) + ' 15:00', '%Y-%m-%d %H:%M')
    if start >= end:
        return 0
    if not (d1_sw_start <= d1 <= d1_sw_end or d1_xw_start <= d1 <= d1_xw_end):
        return 0
    if not (d2_sw_start <= d2 <= d2_sw_end or d2_xw_start <= d2 <= d2_xw_end):
        return 0

    days = (datetime.strptime(str(datetime.date(d2)) + ' 00:00', '%Y-%m-%d %H:%M') - datetime.strptime(
        str(datetime.date(d1)) + ' 00:00', '%Y-%m-%d %H:%M')).days
    minutes = 0
    if days > 1:
        minutes = (days - 1) * 240
    if days == 0:
        if d1_sw_start <= d1 <= d1_sw_end and d1_sw_start <= d2 <= d1_sw_end or d1_xw_start <= d1 <= d1_xw_end and d1_xw_start <= d2 <= d1_xw_end:
            minutes += (d2 - d1).total_seconds() // 60

        if d1_sw_start <= d1 <= d1_sw_end and d1_xw_start <= d2 <= d1_xw_end:
            minutes += (d1_sw_end - d1).total_seconds() // 60
            minutes += (d2 - d1_xw_start).total_seconds() // 60

    else:
        if d1_sw_start <= d1 <= d1_sw_end:
            minutes += 120
            minutes += (d1_sw_end - d1).total_seconds() // 60

        if d1_xw_start <= d1 <= d1_xw_end:
            minutes += (d1_xw_end - d1).total_seconds() // 60

        if d2_sw_start <= d2 <= d2_sw_end:
            minutes += (d2 - d2_sw_start).total_seconds() // 60

        if d2_xw_start <= d2 <= d2_xw_end:
            minutes += 120
            minutes += (d2 - d2_xw_start).total_seconds() // 60

    return int(minutes // freq_count[freq]) + 2
