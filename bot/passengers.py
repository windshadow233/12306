from prettytable import PrettyTable, ALL
from bot.api import api


class Passengers(object):
    """Passengers info"""

    def get_passengers(self, show_no_active=False):
        passengers_info = []
        page = 1
        try:
            while 1:
                data = {
                    "pageIndex": page,
                    "pageSize": 100
                }
                passengers = self.sess.post(api.passengers_url, data=data).json()['data']['datas']
                if not show_no_active:
                    shown_passengers = []
                    for p in passengers:
                        if p['if_receive'] == 'N' and not show_no_active:
                            continue
                        shown_passengers.append(p)
                else:
                    shown_passengers = passengers
                page += 1
                passengers_info.extend(shown_passengers)
                if len(passengers) < 100:
                    break
        except Exception as e:
            print('Network error or not login, please retry or get login first!')
            print('Error: ', e)
            return []
        return passengers_info

    def print_passengers(self, passengers):
        info_table = PrettyTable(['序号', '姓名', '性别', '证件类型', '证件号', '身份类型', '手机号'], hrules=ALL)
        for i, p in enumerate(passengers, 1):
            info_table.add_row([i, p['passenger_name'], p['sex_name'],
                                p['passenger_id_type_name'], p['passenger_id_no'],
                                p['passenger_type_name'], p['mobile_no']])
        print(info_table)
