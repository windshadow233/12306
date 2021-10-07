import urllib
import time
import re
from prettytable import PrettyTable, ALL


class Tickets(object):
    """Ticket info"""
    # 车票信息API
    ticket_info_url = 'https://kyfw.12306.cn/otn/leftTicket/queryY'
    train_types = ['G', 'D', 'K', 'T', 'Z']

    def __init__(self):
        self.station2code = self._get_station_info()
        self.code2station = dict(zip(self.station2code.values(), self.station2code.keys()))

    """车站信息"""
    station_info_url = 'https://www.12306.cn/index/script/core/common/station_name_v10149.js'

    def _get_station_info(self):
        r = self.sess.get(self.station_info_url)
        info = re.findall('([\u4e00-\u9fa5]+)\|([A-Z]+)', r.text)
        return dict(info)

    def _parse_ticket_info(self, ticket_info_str, train_type, show_sold_out=False,
                           min_start_hour=0, max_start_hour=24):
        info = ticket_info_str.split('|')
        secret_str = info[0]  # 加密信息字符串
        train_id = info[3]  # 车次
        has_ticket = info[11]  # 是否有票
        if (train_type is not None and train_id[0] != train_type) or (not show_sold_out and has_ticket != 'Y'):
            return
        remark = info[1]
        from_station_code = info[6]  # 出发站代码
        to_station_code = info[7]  # 到达站代码
        from_station_name = self.code2station[from_station_code]  # 出发站名称
        to_station_name = self.code2station[to_station_code]  # 到达站名称
        date = time.strptime(info[13], "%Y%m%d")  # 出发日期
        date = f'{date.tm_year}-{date.tm_mon:02}-{date.tm_mday:02}'
        start_time = info[8]  # 出发时间
        arrive_time = info[9]  # 到达时间
        cost_time = info[10]  # 历时
        start_h, start_min = start_time.split(':')
        if not min_start_hour <= int(start_h) < max_start_hour:
            return
        cost_h, cost_min = cost_time.split(':')
        add_h = 1 if int(start_min) + int(cost_min) >= 60 else 0
        arrive_h = int(start_h) + int(cost_h) + add_h
        if arrive_h >= 24:
            arrive_time = '次日 ' + arrive_time
        vip_seat = info[32]  # 商务、特等座
        first_class_seat = info[31]  # 一等座
        second_class_seat = info[30]  # 二等座
        advanced_soft_sleep = info[21]  # 高级软卧
        soft_sleep = info[23]  # 软卧
        move_sleep = info[33]  # 动卧
        hard_sleep = info[28]  # 硬卧
        soft_seat = info[24]  # 软座
        hard_seat = info[29]  # 硬座
        no_seat = info[26]  # 无座
        return {
            "train_id": train_id,
            "from_station_code": from_station_code,
            "to_station_code": to_station_code,
            "from_station_name": from_station_name,
            "to_station_name": to_station_name,
            "date": date,
            "start_time": start_time,
            "arrive_time": arrive_time,
            "cost_time": cost_time,
            "vip_seat": vip_seat,
            "first_class_seat": first_class_seat,
            "second_class_seat": second_class_seat,
            "advanced_soft_sleep": advanced_soft_sleep,
            "soft_sleep": soft_sleep,
            "move_sleep": move_sleep,
            "hard_sleep": hard_sleep,
            "soft_seat": soft_seat,
            "hard_seat": hard_seat,
            "no_seat": no_seat,
            "has_ticket": has_ticket,
            "remark": remark,
            "secret_str": secret_str
        }

    def get_ticket_info(self, from_, to_, date=None, train_type=None, show_sold_out=False,
                        min_start_hour=0, max_start_hour=24):
        """
        :param from_: 站名,例如: "合肥南"
        :param to_: 站名,例如: "北京北"
        :param date: %Y-%m-%d,例如: "2021-09-01"
        :param train_type: ['G', 'D', 'K', 'T', 'Z', None]之一
        :param show_sold_out: 是否获取售罄的票
        :param min_start_hour: 最早出发时间
        :param max_start_hour: 最晚出发时间
        """
        assert train_type is None or train_type in self.train_types
        assert min_start_hour < max_start_hour, 'Minimum start hour must be smaller than the maximum.'
        from_ = self.station2code.get(from_)
        to_ = self.station2code.get(to_)
        if not from_ or not to_:
            print('无站点信息!')
            return
        date = date or time.strftime('%Y-%m-%d')
        data = {
            "leftTicketDTO.train_date": date,
            "leftTicketDTO.from_station": from_,
            "leftTicketDTO.to_station": to_,
            "purpose_codes": "ADULT"
        }
        query = urllib.parse.urlencode(data)
        try:
            result = self.sess.get(self.ticket_info_url + f'?{query}').json()['data']['result']
        except Exception as e:
            print('Network error or \'date\' parameter beyond range, please retry or choose another date!')
            print('Error: ', e)
            return []
        tickets = []
        for r in result:
            parsed = self._parse_ticket_info(r, train_type, show_sold_out, min_start_hour, max_start_hour)
            if parsed:
                tickets.append(parsed)
        return tickets

    def print_ticket_info(self, tickets):
        info_table = PrettyTable(['序号', '车次', '出发/到达站', '日期', '出发/到达时间', '历时', '商务座', '一等座', '二等座',
                                  '高级软卧', '软卧', '动卧', '硬卧', '软座', '硬座', '无座', '有票', '备注'], hrules=ALL)
        info_table.padding_width = 0
        for i, ticket in enumerate(tickets, 1):
            row = [i, ticket['train_id']]
            from_to_ = f'始 {ticket["from_station_name"]}\n到 {ticket["to_station_name"]}'
            row.append(from_to_)
            row.append(ticket['date'])
            from_to_time = ticket['start_time'] + '\n' + ticket['arrive_time']
            row.append(from_to_time)
            row.append(ticket['cost_time'])
            vip = ticket['vip_seat'] or '--'
            first = ticket['first_class_seat'] or '--'
            second = ticket['second_class_seat'] or '--'
            advanced_soft = ticket['advanced_soft_sleep'] or '--'
            soft_sleep = ticket['soft_sleep'] or '--'
            move_sleep = ticket['move_sleep'] or '--'
            hard_sleep = ticket['hard_sleep'] or '--'
            soft_seat = ticket['soft_seat'] or '--'
            hard_seat = ticket['hard_seat'] or '--'
            no_seat = ticket['no_seat'] or '--'
            has_ticket = ticket['has_ticket']
            remark = ticket['remark']
            row.extend([vip, first, second, advanced_soft, soft_sleep, move_sleep, hard_sleep,
                        soft_seat, hard_seat, no_seat, has_ticket, remark])
            info_table.add_row(row)
        print(info_table)
