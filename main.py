import requests
import re
import urllib
import os
import time
import json
import base64
from encrypt_ecb import encrypt_passwd


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

        self.station2code = self._get_station_info()
        self.code2station = dict(zip(self.station2code.values(), self.station2code.keys()))
        self.qr_img_dir = '/tmp'
        self.qr_img_file = ''

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
        self.e = 'LplN0j2Cwp6O2g9z2YqkjRorjnP1AEeVwQoNOB1LMPQ'
        self.algID = 'Sp4dvQwR2E'

        # 获取一个RAIL_DEVICEID在后续请求中使用
        self._get_rail_deviceid()
        self.sess.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Referer': 'https://kyfw.12306.cn'
        }
        self.sess.cookies['RAIL_DEVICEID'] = self.rail_device_id
        self.sess.cookies['RAIL_EXPIRATION'] = self.rail_expiration

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
        query = urllib.parse.urlencode(data)
        result = self.sess.get(self.ticket_info_url + f'?{query}').json()['data']['result']
        tickets = [self._parse_ticket_info(r) for r in result]
        return tickets

    def _get_rail_deviceid(self):
        a = self.a + str(int(time.time() * 1000))
        url = (f"https://kyfw.12306.cn/otn/HttpZF/logdevice?algID={self.algID}&hashCode=" + self.e + a).replace(' ', '%20')
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
        return r.json()['result_code'] == 0

    def _get_qr_64(self):
        data = {"appid": "otn"}
        r = self.sess.post(self.qr_url, data=data).json()
        b64_code = r['image']
        qr_uuid = r['uuid']
        img_data = base64.b64decode(b64_code)
        image_file = str(time.time()) + '.jpg'
        with open(os.path.join(self.qr_img_dir, image_file), 'wb') as f:
            f.write(img_data)
        self.qr_img_file = image_file
        return qr_uuid

    def _check_qr(self, qr_uuid):
        data = {
            'RAIL_DEVICEID': self.rail_device_id,
            'RAIL_EXPIRATION': self.rail_expiration,
            'uuid': qr_uuid,
            'appid': 'otn'
        }
        r = self.sess.post(self.check_qr_url, data=data)
        return r

    def qr_login(self):
        qr_uuid = self._get_qr_64()
        while 1:
            r = self._check_qr(qr_uuid).json()
            if r['result_code'] == '2':
                print('二维码扫描成功!')
                break
            elif r['result_code'] == '3':
                print('二维码已过期!')
                self.qr_login()
                return 0
            time.sleep(1)
        r = self.sess.post('https://kyfw.12306.cn/passport/web/auth/uamtk', data={'appid': 'otn'})
        # r = self.sess.post('https://kyfw.12306.cn/otn/uamauthclient, data={'tk': tk})
        return r

    def login(self, username, password):
        cast_num = input("输入身份证后四位:")
        success = self._get_msg_code(username, cast_num)
        if not success:
            print('身份证后四位不匹配!')
            return
        print('验证码发送成功!请坐等...')
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
        if r['result_code'] == 1:
            print("用户名或密码错误")
        elif r['result_code'] == 11:
            print("验证码错误")
        elif r['result_code'] == 0:
            print("登录成功！")
        return r
