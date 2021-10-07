import re
from io import BytesIO
import time
from os import environ
import json
import base64
import matplotlib.pyplot as plt
import threading
from bot.encrypt_ecb import encrypt_passwd

plt.ion()
environ['QT_DEVICE_PIXEL_RATIO'] = '0'
environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
environ['QT_SCREEN_SCALE_FACTOR'] = '1'
environ['QT_SCALE_FACTOR'] = '1'


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
    def __init__(self):
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

        # RAIL_DEVICEID
        self.rail_device_id = ''
        # RAIL_EXPIRATION
        self.rail_expiration = ''

        self._keep_login_thread = None

    """Login & Logout"""
    # 验证码发送API
    msg_code_url = 'https://kyfw.12306.cn/passport/web/getMessageCode'
    # 二维码API
    qr_url = 'https://kyfw.12306.cn/passport/web/create-qr64'
    # 二维码状态API
    check_qr_url = 'https://kyfw.12306.cn/passport/web/checkqr'
    # 登录API
    login_url = 'https://kyfw.12306.cn/passport/web/login'
    # 登出API
    logout_url = 'https://kyfw.12306.cn/otn/login/loginOut'

    def _set_cookies(self):
        """
        获取RAIL_DEVICEID与RAIL_EXPIRATION作为cookies,在后续请求中使用
        """
        self._get_rail_deviceid()
        self.sess.cookies['RAIL_EXPIRATION'] = self.rail_expiration

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
        try:
            if self.check_login():
                print('Already login!')
                return False
            self._set_cookies()
            img_data, qr_uuid = self._get_qr_64()
            if img_data is None:
                return False
            print("QR code generated, scan it with 12306 APP to get login.")
            plt.axis('off')
            plt.imshow(plt.imread(BytesIO(img_data)))
            plt.pause(0.001)
            plt.clf()
            while 1:
                r = self._check_qr(qr_uuid).json()
                if r['result_code'] not in '01':
                    print(r['result_message'])
                if r['result_code'] != '0':
                    plt.close()
                if r['result_code'] == '2':
                    plt.close()
                    break
                elif r['result_code'] == '1':
                    pass
                elif r['result_code'] != '0':
                    return False
                time.sleep(1)
            return self._uamauth()
        except Exception as e:
            print('Network error, please retry!')
            print('Error: ', e)
            return False

    def sms_login(self, username, password, cast_num):
        """
        通过验证码、手机和密码登录,有每日次数限制
        """
        if self.check_login():
            print('Already login!')
            return
        self._set_cookies()
        msg = self._get_msg_code(username, cast_num)
        print(msg)
        if msg != 'Obtain mobile verification code successfully！':
            return
        print('Please wait...')
        rand_code = input('Input code:')
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
            print('Logout successfully!')
            self.sess.get(self.logout_url)
        else:
            print('Not login yet!')
        if isinstance(self._keep_login_thread, StoppableThread) and self._keep_login_thread.is_alive():
            self._keep_login_thread.stop()

    def check_login(self):
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        r = self.sess.post(url, data={"_json_att": ""}).json()
        return r["data"]['flag']
