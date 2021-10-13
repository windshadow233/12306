import urllib
import time
import re
import json
import js2py
from prettytable import PrettyTable, ALL
from bot.api import api


class Order(object):

    seat_type_dict = {
        'O': '二等座',
        'M': '一等座',
        '9': '商务座',
        '3': '硬卧',
        '1': '硬座',
        '4': '软卧'
    }
    ticket_type_dict = {
        '1': '成人票',
        '2': '儿童票',
        '3': '学生票',
        '4': '残军票'
    }
    seat_type_to_code = dict(zip(seat_type_dict.values(), seat_type_dict.keys()))
    ticket_type_to_code = dict(zip(ticket_type_dict.values(), ticket_type_dict.keys()))
    seat_type_choice = {
        '1': ['O', 'M', '9', '3', '1', '4'],
        '2': ['O', 'M', '9', '3', '1', '4'],
        '3': ['O', '3', '1'],
        '4': ['O', 'M', '9', '3', '1', '4']
    }
    seat_number_choice = {
        "M": ['A', 'C', 'D', 'F'],
        "O": ['A', 'B', 'C', 'D', 'F'],
        "9": ['A', 'C', 'F']
    }

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
            r = self.sess.post(api.submit_order_request_url, data=data).json()
        except Exception as e:
            print('Network error or not login, please retry or get login first!')
            print('Error: ', e)
            return False, None
        status = r['status']
        return status, r

    def get_init_info(self):
        """初始化车票下单页面信息"""
        r = self.sess.get(api.init_dc_url)
        form = re.search('ticketInfoForPassengerForm=(.+)', r.text).groups()[0][:-1].replace('\'', '"')
        form = json.loads(form)
        self.__setattr__('ticketInfoForPassengerForm', form)
        self.__setattr__('submit_token', re.findall('globalRepeatSubmitToken = \'(.*)\'', r.text)[0])

    def generate_passenger_ticket_str(self, passenger, seat_type, ticket_type):
        s_list = [seat_type, '0', ticket_type, passenger['passenger_name'], passenger['passenger_id_type_code'],
                  passenger['passenger_id_no'], passenger['mobile_no'] or "", 'N', passenger['allEncStr']]
        return ','.join(s_list)

    def generate_old_passenger_str(self, passenger):
        s_list = [passenger['passenger_name'], passenger['passenger_id_type_code'], passenger['passenger_id_no'],
                  passenger['passenger_type']]
        return ','.join(s_list)

    def check_order_info(self, passenger_strs, passenger_old_strs):
        bed_level_order_num = '000000000000000000000000000000'
        cancel_flag = '2'
        tour_flag = 'dc'
        rand_code = ""
        csessionid = ""
        sig = "",
        scene = "nc_login"
        _json_att = ""
        s = '_'.join(passenger_strs)
        old_s = '_'.join(passenger_old_strs) + '_'
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
            "REPEAT_SUBMIT_TOKEN": self.__getattribute__('submit_token')
        }
        r = self.sess.post(api.check_order_info_url, data=data).json()
        return r['status'], r

    def print_orders(self, order_info):
        table = PrettyTable(['序号', '票种', '席别', '姓名', '证件类型',
                             '证件号码', '手机号码', '选座'], hrules=ALL)
        for i, order in enumerate(order_info, 1):
            passenger = order['passenger']
            row = [i, self.ticket_type_dict[order['ticket_type']], self.seat_type_dict[order['seat_type']],
                   passenger['passenger_name'], passenger['passenger_id_type_name'], passenger['passenger_id_no'],
                   passenger['mobile_no'], order["choose_seat"] or '--']
            table.add_row(row)
        print(table)

    def get_queue_count(self, seat_type):
        form = self.__getattribute__('ticketInfoForPassengerForm')
        order_info = form['orderRequestDTO']
        train_date = order_info['train_date']['time']
        data = {
            "train_date": js2py.eval_js(f'new Date({train_date}).toString()'),
            "train_no": order_info['train_no'],
            "stationTrainCode": order_info['station_train_code'],
            "seatType": seat_type,
            "fromStationTelecode": order_info['from_station_telecode'],
            "toStationTelecode": order_info['to_station_telecode'],
            "leftTicket": form['queryLeftTicketRequestDTO']['ypInfoDetail'],
            "purpose_codes": form['purpose_codes'],
            "train_location": form['train_location'],
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.__getattribute__('submit_token')
        }
        r = self.sess.post(api.queue_count_url, data=data).json()
        return r['status'], r

    def confirm_single_for_queue(self, passenger_strs, passenger_old_strs, seats):
        form = self.__getattribute__('ticketInfoForPassengerForm')
        data = {
            "passengerTicketStr": '_'.join(passenger_strs),
            "oldPassengerStr": '_'.join(passenger_old_strs) + '_',
            "randCode": "",
            "purpose_codes": form["purpose_codes"],
            "key_check_isChange": form["key_check_isChange"],
            "leftTicketStr": form['queryLeftTicketRequestDTO']['ypInfoDetail'],
            "train_location": form['train_location'],
            "choose_seats": seats,
            "seatDetailType": "000",
            "is_jy": "N",
            "is_cj": "N",
            "whatsSelect": "1",
            "roomType": "00",
            "dwAll": "N",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.__getattribute__('submit_token')
        }
        r = self.sess.post(api.confirm_url, data=data).json()
        return r['status'], r
