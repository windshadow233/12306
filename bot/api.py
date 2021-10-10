class API(object):
    """login"""
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
    # rail_device_id API
    device_id_url = 'https://12306-rail-id-v2.pjialin.com/'
    # uamtk API
    uamtk_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
    # uamauthclient
    uamauthclient_url = 'https://kyfw.12306.cn/otn/uamauthclient'
    # 检查登录状态
    check_login_url = 'https://kyfw.12306.cn/otn/login/checkUser'

    """ticket information"""
    # 查票主页链接
    ticket_home_url = 'https://kyfw.12306.cn/otn/leftTicket/init'
    # 车站信息API
    station_info_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
    # 车票信息API
    ticket_info_url = 'https://kyfw.12306.cn/otn/{}'

    """passengers"""
    # 乘客信息 API
    passengers_url = 'https://kyfw.12306.cn/otn/passengers/query'

    """order"""
    # SubmitOrderRequest
    submit_order_request_url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
    # checkOrderInfo
    check_order_info_url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
    init_dc_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
    # 余票查询
    queue_count_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
    # 提交订单
    confirm_url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'


api = API()
