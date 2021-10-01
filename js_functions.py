def qb(a):
    b = a.split(".")
    if len(b) != 4:
        raise RuntimeError("Invalid format -- expecting a.b.c.d")
    a = 0
    for c, d in enumerate(b):
        d = int(d)
        assert 0 < d < 255, "Each octet must be between 0 and 255"
        a |= d << 8 * (len(b) - c - 1)
        a >>= 0
    return a

0: l {key: 'adblock', value: '0'}
1: l {key: 'appCodeName', value: 'Mozilla'}
2: l {key: 'appMinorVersion', value: ''}
3: l {key: 'appName', value: 'Netscape'}
4: l {key: 'browserLanguage', value: 'zh-CN'}
5: l {key: 'cookieCode', value: 'new'}
6: l {key: 'cookieCode', value: 'new'}
8: l {key: 'cookieEnabled', value: '1'}
9: l {key: 'cpuClass', value: ''}
10: l {key: 'custID', value: '133'}
11: l {key: 'doNotTrack', value: 'unknown'}
12: l {key: 'flashVersion', value: 0}
13: l {key: 'hasLiedBrowser', value: 'false'}
14: l {key: 'hasLiedLanguages', value: 'false'}
15: l {key: 'hasLiedOs', value: 'false'}
16: l {key: 'hasLiedResolution', value: 'false'}
17: l {key: 'historyList', value: 7}
18: l {key: 'indexedDb', value: '1'}
19: l {key: 'javaEnabled', value: '0'}
20: l {key: 'jsFonts', value: 'b5814a5b6c93145a88ee1cd0e93ee648'}
21: l {key: 'localStorage', value: '1'}
22: l {key: 'mimeTypes', value: 'fe9c964a38174deb6891b6523b8e4518'}
23: l {key: 'onLine', value: 'true'}
24: l {key: 'openDatabase', value: '1'}
25: l {key: 'os', value: 'Linux x86_64'}
26: l {key: 'platform', value: 'WEB'}
27: l {key: 'plugins', value: '1412399caf7126b9506fee481dd0a407'}
28: l {key: 'scrAvailHeight', value: '1053'}
29: l {key: 'scrAvailWidth', value: '1920'}
30: l {key: 'scrColorDepth', value: '24'}
31: l {key: 'scrDeviceXDPI', value: ''}
32: l {key: 'scrHeight', value: '1080'}
33: l {key: 'scrWidth', value: '1920'}
34: l {key: 'sessionStorage', value: '1'}
35: l {key: 'systemLanguage', value: ''}
36: l {key: 'timeZone', value: -8}
37: l {key: 'touchSupport', value: '99115dfb07133750ba677d055874de87'}
38: l {key: 'userAgent', value: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36…ML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
39: l {key: 'userLanguage', value: ''}
40: l {key: 'webSmartID', value: '5104a1eeeac7de06f770c7aa2ce15054'}
class l:
    def __init__(self, key, value):
        self.key = key
        self.value = value