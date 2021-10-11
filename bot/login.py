import time
import json
import getpass
import requests
import base64
import threading
import platform
import qrcode
from bot.encrypt_ecb import encrypt_passwd
from bot.api import api


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Login(object):

    rail_device_id = ''
    rail_expiration = ''
    _keep_login_thread = None

    """Login & Logout"""

    def _get_rail_deviceid(self):
        r = requests.get(api.device_id_url).json()['id']
        url = base64.b64decode(r).decode()
        r = self.sess.get(url).text
        result = '{}'
        if r.find('callbackFunction') >= 0:
            result = r[18:-2]
        result = json.loads(result)
        self.sess.cookies.update({
            'RAIL_EXPIRATION': result.get('exp'),
            'RAIL_DEVICEID': result.get('dfp'),
        })

    def _get_msg_code(self, username, cast_num):
        data = {
            "appid": "otn",
            "username": username,
            "castNum": cast_num
        }
        r = self.sess.post(api.msg_code_url, data=data)
        return r.json()['result_message']

    def _get_qr_64(self):
        data = {"appid": "otn"}
        r = self.sess.post(api.qr_url, data=data).json()
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
        r = self.sess.post(api.check_qr_url, data=data)
        return r

    def _uamauth(self):
        r = self.sess.post(api.uamtk_url, data={'appid': 'otn'}).json()
        print(r['result_message'])
        if r['result_code'] == 0:
            apptk = r['newapptk']
            r = self.sess.post(api.uamauthclient_url, {'tk': apptk}).json()
            if r['result_code'] == 0:
                print(f'Login successfully! Welcome, {r["username"]}!')

                def keep_login():
                    thread = threading.current_thread()
                    urls = ['https://www.12306.cn/index/index.html',
                            'https://kyfw.12306.cn/otn/view/index.html']
                    i = 0
                    while not thread.stopped():
                        self.sess.get(urls[i])
                        i = 1 - i
                        time.sleep(10)

                self._keep_login_thread = StoppableThread(target=keep_login, name='Keep Login', daemon=True)
                self._keep_login_thread.start()
            else:
                print(r['result_message'])
        return r['result_code'] == 0

    def qr_login(self):
        """
        扫描二维码登录
        """
        if self.check_user()[0]:
            print('Already login!')
            return False
        self._get_rail_deviceid()
        img_data, qr_uuid = self._get_qr_64()
        if img_data is None:
            return False
        print("QR code generated, scan it with 12306 APP to get login.")
        qr_login_url = api.qr_login_url + f'?loginUUID={qr_uuid}'
        if 'Windows' not in platform.platform():
            qr = qrcode.QRCode(border=2)
            qr.add_data(qr_login_url)
            qr.print_ascii(invert=True)
        else:
            img = qrcode.make(data=qr_login_url)
            img.show()
        scan_print_flat = False
        while 1:
            r = self._check_qr(qr_uuid).json()
            code = r['result_code']
            if code != '0':
                if code == '1':
                    if not scan_print_flat:
                        scan_print_flat = True
                        print('二维码扫描成功，请授权登录。')
                else:
                    print(r['result_message'])
            if code == '2':
                break
            elif code == '1':
                pass
            elif code != '0':
                return False
            time.sleep(1)
        return self._uamauth()

    def sms_login(self, username):
        """
        通过验证码、手机和密码登录,有每日次数限制
        """
        if self.check_user()[0]:
            print('Already login!')
            return
        self._get_rail_deviceid()
        cast_num = input('Input the last 4 digits of your ID card:')
        msg = self._get_msg_code(username, cast_num)
        print(msg)
        if msg != '获取手机验证码成功！':
            return
        password = getpass.getpass('While waiting for the verification code, please input your password:')
        rand_code = input('Input verification code:')
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
        r = self.sess.post(api.login_url, data=data).json()
        print(r['result_message'])
        if r['result_code'] != 0:
            return
        return self._uamauth()

    def logout(self):
        print('Logout successfully!')
        self.sess.get(api.logout_url)
        if isinstance(self._keep_login_thread, StoppableThread) and self._keep_login_thread.is_alive():
            self._keep_login_thread.stop()

    def check_user(self):
        r = self.sess.post(api.check_user_url).json()
        data = r['data']
        return data['is_login'] == 'Y', data.get('name')
