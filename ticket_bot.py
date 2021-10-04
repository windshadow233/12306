import requests
import re
import urllib
from io import BytesIO
import time
from os import environ
import json
import base64
import matplotlib.pyplot as plt
import threading
from prettytable import PrettyTable
from encrypt_ecb import encrypt_passwd

plt.ion()
environ['QT_DEVICE_PIXEL_RATIO'] = '0'
environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
environ['QT_SCREEN_SCALE_FACTOR'] = '1'
environ['QT_SCALE_FACTOR'] = '1'


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class RailWayTicket(object):
    def __init__(self):
        self.sess = requests.session()
        self.sess.get('https://kyfw.12306.cn')
        # 车站信息
        self.station_info_url = 'https://www.12306.cn/index/script/core/common/station_name_v10149.js'
        # 车票信息API
        self.ticket_info_url = 'https://kyfw.12306.cn/otn/leftTicket/queryY'
        # 验证码发送API
        self.msg_code_url = 'https://kyfw.12306.cn/passport/web/getMessageCode'
        # 二维码API
        self.qr_url = 'https://kyfw.12306.cn/passport/web/create-qr64'
        # 二维码状态API
        self.check_qr_url = 'https://kyfw.12306.cn/passport/web/checkqr'
        # 登录API
        self.login_url = 'https://kyfw.12306.cn/passport/web/login'
        # 登出API
        self.logout_url = 'https://kyfw.12306.cn/otn/login/loginOut'
        # 乘客信息
        self.passengers_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'

        self.station2code = self._get_station_info()
        self.code2station = dict(zip(self.station2code.values(), self.station2code.keys()))

        self.train_types = ['G', 'D', 'K', 'T', 'Z']

        # RAIL_DEVICEID
        self.rail_device_id = ''
        # RAIL_EXPIRATION
        self.rail_expiration = ''

        # 获取 RAIL_DEVICEID需要的参数，可写死。
        self.a = '&FMQw=0&q4f3=zh-CN&VySQ=FGH3fUJQ2Z0U-UKS73G-NLHmiI6FVlCp&' \
                 'VPIf=1&custID=133&VEek=unknown&dzuS=0&yD16=0&' \
                 'EOQP=b5814a5b6c93145a88ee1cd0e93ee648&jp76=fe9c964a38174deb6891b6523b8e4518&' \
                 'hAqN=Linux x86_64&platform=WEB&ks0Q=1412399caf7126b9506fee481dd0a407&TeRS=1053x1920&' \
                 'tOHY=24xx1080x1920&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&' \
                 '0aew=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36&' \
                 'E3gR=5104a1eeeac7de06f770c7aa2ce15054&timestamp='
        self.e = 'LplN0j2Cwp6O2g9z2YqkjRorjnP1AEeVwQoNOB1LMPQ'  # e由HashAlg算法生成，该算法时不时发生变化，正在考虑如何破解
        self.algID = 'Sp4dvQwR2E'

        self.sess.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn',
            'Origin': 'https://kyfw.12306.cn'
        }
        self._keep_login_thread = None

    def _set_cookies(self):
        """
        获取RAIL_DEVICEID与RAIL_EXPIRATION作为cookies,在后续请求中使用
        """
        self._get_rail_deviceid()
        self.sess.cookies['RAIL_EXPIRATION'] = self.rail_expiration

    def _get_station_info(self):
        r = self.sess.get(self.station_info_url)
        info = re.findall('([\u4e00-\u9fa5]+)\|([A-Z]+)', r.text)
        return dict(info)

    def _parse_ticket_info(self, ticket_info_str, train_type):
        info = ticket_info_str.split('|')
        train_id = info[3]  # 车次
        if train_type is not None and train_id[0] != train_type:
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
        time_cost = info[10]  # 历时
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
        has_ticket = info[11]  # 是否有票
        return {
            "train_id": train_id,
            "from_station_code": from_station_code,
            "to_station_code": to_station_code,
            "from_station_name": from_station_name,
            "to_station_name": to_station_name,
            "date": date,
            "start_time": start_time,
            "arrive_time": arrive_time,
            "time_cost": time_cost,
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
            "remark": remark
        }

    def get_ticket_info(self, from_, to_, date=None, train_type=None):
        """
        :param from_: 站名,例如: "合肥南"
        :param to_: 站名,例如: "北京北"
        :param date: %Y-%m-%d,例如: "2021-09-01"
        :param train_type: ['G', 'D', 'K', 'T', 'Z', None]之一
        """
        assert train_type is None or train_type in self.train_types
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
        result = self.sess.get(self.ticket_info_url + f'?{query}').json()['data']['result']
        tickets = []
        for r in result:
            parsed = self._parse_ticket_info(r, train_type)
            if parsed:
                tickets.append(parsed)
        return tickets

    def print_ticket_info(self, tickets):
        info_table = PrettyTable(['序号', '车次', '出发/到达站', '日期', '出发/到达时间', '历时', '商务座', '一等座', '二等座',
                                  '高级软卧', '软卧', '动卧', '硬卧', '软座', '硬座', '无座', '有票', '备注'])
        info_table.padding_width = 0
        for i, ticket in enumerate(tickets, 1):
            row = [i, ticket['train_id']]
            from_to_ = f'始 {ticket["from_station_name"]}\n到 {ticket["to_station_name"]}'
            row.append(from_to_)
            row.append(ticket['date'])
            from_to_time = ticket['start_time'] + '\n' + ticket['arrive_time']
            row.append(from_to_time)
            row.append(ticket['time_cost'])
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

    def _get_rail_deviceid(self):
        a = self.a + str(int(time.time() * 1000))
        url = (f"https://kyfw.12306.cn/otn/HttpZF/logdevice?algID={self.algID}&hashCode=" + self.e + a).replace(' ',
                                                                                                                '%20')
        r = self.sess.get(url)
        data = json.loads(re.search('{.+}', r.text).group())
        self.rail_device_id = data.get('dfp')
        self.rail_expiration = data.get('exp')

    def _get_msg_code(self, username, cast_num):
        data = {
            "appid": "otn",
            "username": username,
            "castNum": cast_num
        }
        r = self.sess.post(self.msg_code_url, data=data)
        return r.json()['result_message']

    def _get_qr_64(self):
        data = {"appid": "otn"}
        r = self.sess.post(self.qr_url, data=data).json()
        b64_code = r['image']
        qr_uuid = r['uuid']
        img_data = base64.b64decode(b64_code)
        return img_data, qr_uuid

    def _check_qr(self, qr_uuid):
        data = {
            'RAIL_DEVICEID': self.rail_device_id,
            'RAIL_EXPIRATION': self.rail_expiration,
            'uuid': qr_uuid,
            'appid': 'otn'
        }
        r = self.sess.post(self.check_qr_url, data=data)
        return r

    def _uamauth(self):
        r = self.sess.post('https://kyfw.12306.cn/passport/web/auth/uamtk', data={'appid': 'otn'}).json()
        print(r['result_message'])
        if r['result_code'] == 0:
            apptk = r['newapptk']
            r = self.sess.post('https://kyfw.12306.cn/otn/uamauthclient', {'tk': apptk}).json()
            if r['result_code'] == 0:
                print(f'登录成功! {r["username"]}, 欢迎您!')

                def keep_login():
                    thread = threading.current_thread()
                    while not thread.stopped():
                        self.sess.get('https://kyfw.12306.cn/otn/view/index.html')
                        time.sleep(10)

                self._keep_login_thread = StoppableThread(target=keep_login, name='Keep Login', daemon=True)
                self._keep_login_thread.start()
            else:
                print(r['result_message'])
        return r

    def qr_login(self):
        """
        扫描二维码登录
        """
        if self.check_login():
            print('当前已是登录状态!')
            return
        self._set_cookies()
        img_data, qr_uuid = self._get_qr_64()
        print("二维码已生成，请用12306 APP扫码登录")
        plt.axis('off')
        plt.imshow(plt.imread(BytesIO(img_data)))
        plt.pause(0.001)
        plt.clf()
        while 1:
            r = self._check_qr(qr_uuid).json()
            print(r['result_message'])
            if r['result_code'] == '2':
                plt.close()
                break
            elif r['result_code'] != '0':
                plt.close()
                return
            time.sleep(1)
        self._uamauth()

    def sms_login(self, username, password, cast_num):
        """
        通过验证码、手机和密码登录,有每日次数限制
        """
        if self.check_login():
            print('当前已是登录状态!')
            return
        self._set_cookies()
        msg = self._get_msg_code(username, cast_num)
        print(msg)
        if msg != '获取手机验证码成功！':
            return
        print('请坐等...')
        rand_code = input('输入验证码:')
        data = {
            "sessionid": "",
            "sig": "",
            "if_check_slide_passcode_token": "",
            "scene": "",
            "checkMode": 0,
            "randCode": rand_code,
            "username": username,
            "password": encrypt_passwd(password),
            "appid": "otn"
        }
        r = self.sess.post(self.login_url, data=data).json()
        print(r['result_message'])
        if not r['result_code']:
            return
        self._uamauth()

    def logout(self):
        if self.check_login():
            self.sess.get(self.logout_url)
            print('登出成功!')
        else:
            print('当前尚未登录!')
        if isinstance(self._keep_login_thread, StoppableThread) and self._keep_login_thread.is_alive():
            self._keep_login_thread.stop()

    def check_login(self):
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        r = self.sess.post(url).json()
        return r["data"]['flag']

    def get_passengers(self):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        r = self.sess.post(url)
        submit_token = re.search('globalRepeatSubmitToken = \'(.+)\'', r.text).groups()[0]
        passengers_info = self.sess.post(self.passengers_url, data={'REPEAT_SUBMIT_TOKEN': submit_token,
                                                                    '_json_att': ''}).json()
        return passengers_info['data']['normal_passengers']


if __name__ == "__main__":
    bot = RailWayTicket()
    bot.qr_login()
