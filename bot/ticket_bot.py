import requests
import re
import urllib
import time
from prettytable import PrettyTable, ALL
from bot.login import Login
from bot.passengers import Passengers
from bot.tickets import Tickets


class RailWayTicketBot(Login, Passengers, Tickets):
    def __init__(self):
        self.sess = requests.session()
        self.sess.get('https://kyfw.12306.cn')
        Login.__init__(self)
        Passengers.__init__(self)
        Tickets.__init__(self)

        self.code2seat = {
            'O': '二等座',
            'M': '一等座',
            'P': '特等座',
            '9': '商务座'
        }
        self.code2ticket = {
            '1': '成人票',
            '2': '儿童票',
            '3': '学生票',
            '4': '残军票'
        }

        self.train_types = ['G', 'D', 'K', 'T', 'Z']

        self.sess.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn',
            'Origin': 'https://kyfw.12306.cn'
        }

    """SubmitOrderRequest"""
    submit_order_request_url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'

    def submit_order_request(self, ticket):
        data = {
            "secretStr": urllib.parse.unquote(ticket.get('secret_str')),
            "train_date": ticket.get('date'),
            "back_train_date": time.strftime("%Y-%m-%d"),
            "tour_flag": "dc",  # 单程
            "purpose_codes": "ADULT",  # 成人票
            "query_from_station_name": ticket.get('from_station_name'),
            "query_to_station_name": ticket.get('to_station_name'),
            "undefined": ""
        }
        try:
            r = self.sess.post(self.submit_order_request_url, data=data).json()
        except Exception as e:
            print('Network error or not login, please retry or get login first!')
            print('Error: ', e)
            return False
        status = r['status']
        if status:
            print('Submit successfully!')
        else:
            print(r['messages'][0])
        return r['status']

    """checkOrderInfo"""
    check_order_info_url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
    init_dc_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
    REPEAT_SUBMIT_TOKEN = ''

    def print_order_info(self, order_info):
        table = PrettyTable(['序号', '票种', '席别', '姓名', '证件类型',
                             '证件号码', '手机号码'], hrules=ALL)
        for i, order in enumerate(order_info, 1):
            info = order['info']
            row = [i, self.code2ticket[order['ticket_type']], self.code2seat[order['seat_type']],
                   info['passenger_name'], info['passenger_id_type_name'], info['passenger_id_no'],
                   info['mobile_no']]
            table.add_row(row)
        print(table)

    def _get_global_repeat_submit_token(self):
        r = self.sess.get(self.init_dc_url)
        token = re.search('globalRepeatSubmitToken = \'(.+)\'', r.text).groups()[0]
        self.REPEAT_SUBMIT_TOKEN = token
        return token

    def _generate_passenger_ticket_str(self, passenger, seat_type, ticket_type):
        s_list = [seat_type, '0', ticket_type, passenger['passenger_name'], passenger['passenger_id_type_code'],
                  passenger['passenger_id_no'], passenger['mobile_no'] or "", 'N', passenger['allEncStr']]
        return ','.join(s_list)

    def _generate_old_passenger_str(self, passenger):
        s_list = [passenger['passenger_name'], passenger['passenger_id_type_code'], passenger['passenger_id_no'],
                  passenger['passenger_type']]
        return ','.join(s_list) + '_'

    def _check_order_info(self, passenger_seat_ticket_triples):
        self._get_global_repeat_submit_token()
        bed_level_order_num = '000000000000000000000000000000'
        cancel_flag = '2'
        tour_flag = 'dc'
        rand_code = ""
        csessionid = ""
        sig = "",
        scene = "nc_login"
        _json_att = ""
        s = []
        old_s = ''
        for passenger, seat, ticket in passenger_seat_ticket_triples:
            s.append(self._generate_passenger_ticket_str(passenger, seat, ticket))
            old_s += self._generate_old_passenger_str(passenger)
        s = '_'.join(s)
        data = {
            "cancel_flag": cancel_flag,
            "bed_level_order_num": bed_level_order_num,
            "passengerTicketStr": s,
            "oldPassengerStr": old_s,
            "tour_flag": tour_flag,
            "randCode": rand_code,
            "whatsSelect": 1,
            "sessionId": csessionid,
            "sig": sig,
            "scene": scene,
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.REPEAT_SUBMIT_TOKEN
        }
        r = self.sess.post(self.check_order_info_url, data=data)
        return r


if __name__ == "__main__":
    bot = RailWayTicketBot()
    bot.qr_login()
