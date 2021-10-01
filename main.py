import requests
import re
import urllib


class RailWayTicket(object):
    def __init__(self):
        self.sess = requests.session()
        self.sess.get('https://kyfw.12306.cn')
        self.station_info_url = 'https://www.12306.cn/index/script/core/common/station_name_v10149.js'
        self.ticket_info_url = 'https://kyfw.12306.cn/otn/leftTicket/queryY'
        self.verify_url = 'https://kyfw.12306.cn/passport/web/slide-passcode'

        self.station2code = self._get_station_info()
        self.code2station = dict(zip(self.station2code.values(), self.station2code.keys()))

    def _get_station_info(self):
        r = self.sess.get(self.station_info_url)
        info = re.findall('([\u4e00-\u9fa5]+)\|([A-Z]+)', r.text)
        return dict(info)

    def _parse_ticket_info(self, ticket_info_str):
        info = ticket_info_str.split('|')
        train_id = info[3]  # 车次
        from_station_code = info[6]  # 出发站代码
        to_station_code = info[7]  # 到达站代码
        from_station_name = self.code2station[from_station_code]  # 出发站名称
        to_station_name = self.code2station[to_station_code]  # 到达站名称
        start_time = info[8]  # 出发时间
        arrive_time = info[9]  # 到达时间
        time_cost = info[10]  # 历时
        vip_seat = info[32]  # 商务、特等座
        first_class_seat = info[31]  # 一等座
        second_class_seat = info[30]  # 二等座
        soft_sleep = info[23]  # 软卧
        hard_sleep = info[28]  # 硬卧
        hard_seat = info[29]  # 硬座
        no_seat = info[26]  # 无座
        return {
            "train_id": train_id,
            "from_station_code": from_station_code,
            "to_station_code": to_station_code,
            "from_station_name": from_station_name,
            "to_station_name": to_station_name,
            "start_time": start_time,
            "arrive_time": arrive_time,
            "time_cost": time_cost,
            "vip_seat": vip_seat,
            "first_class_seat": first_class_seat,
            "second_class_seat": second_class_seat,
            "soft_sleep": soft_sleep,
            "hard_sleep": hard_sleep,
            "hard_seat": hard_seat,
            "no_seat": no_seat
        }

    def _get_ticket_info(self):
        data = {
            "leftTicketDTO.train_date": "2021-10-04",
            "leftTicketDTO.from_station": "BJP",
            "leftTicketDTO.to_station": "SHH",
            "purpose_codes": "ADULT"
        }
        headers = {
            "Host": "kyfw.12306.cn",
            "Referer": "https://kyfw.12306.cn/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
        }
        query = urllib.parse.urlencode(data)
        result = self.sess.get(self.ticket_info_url + f'?{query}', headers=headers).json()['data']['result']
        tickets = [self._parse_ticket_info(r) for r in result]
        return tickets

    def _get_rail_deviceid(self):
        e = ''
        a = ''
        r = self.sess.get('https://kyfw.12306.cn/otn/HttpZF/GetJS')
        algID = re.search(r'algID\\x3\w+', r.text).group()[7:]  # 这玩意会动态改变，所以用session请求获取一下
        url = f"https://kyfw.12306.cn/otn/HttpZF/logdevice?algID={algID}&hashCode=" + e + a
        return url

    def _get_verify_code(self, username):
        data = {
            "username": username,
            "appid": "otn",
            "slideMode": "1"
        }
        r = self.sess.post(self.verify_url, data=data)
        return r


bot = RailWayTicket()
