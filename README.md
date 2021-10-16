# 一个简陋的12306命令行客户端

此项目仅供学习、娱乐

若出现网络问题或一些奇怪的报错，大概率是12306自身的问题，重新进入程序或多次重试一般即可成功，若仍失败，可能网络环境有问题，考虑重启、重连WiFi等。

若遇到扫码登录无反应、系统错误或授权失败等情况，请使用组合键Ctrl + C断开命令，并重新使用```login```命令。

## 支持功能

- [x] 登录
  - [x] 扫二维码
  - [x] 手机验证码
  - [ ] 滑块
- [x] 查票
  - [x] 筛选列车类型
  - [x] 筛选发车时间
  - [x] 筛选有票车次
- [x] 获取乘车人信息
- [x] 添加乘车人
  - [x] 选择车票类型
    - [x] 成人票
    - [x] 学生票
    - [x] 儿童票
    - [x] 残军票
  - [x] 选择席位类型
    - [x] 一等座
    - [x] 二等座
    - [x] 特等、商务座
    - [x] 硬卧
    - [x] 硬座
    - [x] 软卧
    - [ ] 高级软卧
    - [ ] 动卧
    - [ ] 软座
  - [x] 选座
- [x] 余票查询
- [x] 提交订单
- [x] 通过配置文件自动买票（模板见config.yml）
  - [x] 完全匹配站点名
  - [x] 指定列车类型
  - [x] 限定发车时间范围
  - [x] 指定期望发车时间
  - [x] 指定发车时间顺延策略
  - [x] 车票过期自动刷新
  - [x] 多乘车人
  - [x] 车票类型、座位类型、座位号选择
- [ ] 优化抢票速度
- [ ] 候补（不打算搞，感觉都候补了也没必要用脚本）


## 环境安装
```shell
$ conda create -n 12306 python=3.7
$ conda activate 12306
$ git clone https://github.com/windshadow233/12306.git
$ cd 12306
$ pip install -r requirements.txt
```

## 使用方法
```shell
$ conda activate 12306
$ cd 12306
$ python cmd_tools.py
```
以上命令将会进入以下命令环境:
```
Welcome to the 12306 command line tool. Type help or ? to list commands.
You're required a stable network environment to use this tool.
BTW, you'd better use this tool in full screen mode.
(12306)>
```
当前支持的命令有:

- ```login```
  登录，目前支持用12306 APP扫码登录、账号密码（需手机验证码）登录。
- ```logout```
  登出
- ```search```
  搜索票务信息(此功能无需登录)
- ```get_passengers```
  获取乘客信息
- ```show```
  打印指定内容
- ```clear```
  清除指定内容
- ```check_user```
  检查当前登录状态
- ```select_ticket```
  在搜索结果中选择车票
- ```update_tickets```
  更新票务信息(搜索参数来自上一次搜索)
- ```add_order```
  添加订单信息(可选座)
- ```rm_order```
  删除订单信息
- ```queue_count```
  余票查询
- ```confirm```
  确认并提交订单
- ```auto_run```
  通过配置文件自动刷票
- ```bye```
  退出命令行

另有一些其他自带的命令。

详情以及命令的参数请使用```help```或```-h```查看。
## 手动订票流程

1. ```login```(登录)
2. ```search```(查票)
3. ```select_ticket```(选票)
4. ```add_order```(添加订单)
5. ```queue_count```(余票查询)
6. ```confirm```(提交订单)

## 自动订票流程
1. 根据订票需求，按照给定模板提前编辑好yml文件，放置于工作目录下
2. 在工作目录下运行程序
3. 运行 ```auto_run```命令，即可全自动订票
## 简单示例
```
(12306)>login
QR code generated, scan it with 12306 APP to get login.
█████████████████████████████████████████████████████████
██ ▄▄▄▄▄ █▀█▄██  ▄ ▀ █▀ ▄███▀ ▄▀▄▄▄  ▄ ▄ ▀▄▀ ▀██ ▄▄▄▄▄ ██
██ █   █ █ ▀██▄ ▄▄ ▀▄ ▀█▀▄▀▄ ▄██▄▀ █ ▀▀ ▀ ▀▀▀▄▀█ █   █ ██
██ █▄▄▄█ ██▄▄▀█▄▀▀▄▄▀ █▄▄▄ ▄▄▄     █▀▀ █▀▀▄█ ███ █▄▄▄█ ██
██▄▄▄▄▄▄▄█ █▄▀▄▀ █▄█ ▀▄▀▄█ █▄█ █▄█▄▀▄█▄▀ ▀▄▀▄▀▄█▄▄▄▄▄▄▄██
██▄▀██▀▀▄▀ █ ▀█▀█ █ ▀▀███▄▄ ▄▄   ▀▀▀ ▄   ▀▀  ▀ ▄ ▀█ ▄ ███
██ ▀  ▀ ▄█▄▄  ▄█▀▀▄ ██ ▄▀▀▀ ▄██▀▄▀█ ▄ █▀▄█▀██ ▄█▄▀▄ ▄████
██▀█▄█▀▀▄  █▄  █▄██▀▀▄▄▀▄▄▀ █▀  ██  ▄ ▄▀▄  ▀  █ ██ ▄█ ▀██
██ ▀▀ ▄█▄█▀ ▀  ▄▄█▄██▀█▀▀▀▀  ▀█▀▄▀█▄▀█▄██▄█▀█▀█▀▄▀▀█▀▀███
███▄▄ █▀▄█ ▄█ █▄█▄ ▄   ██ █▀▄█  ▀▄▀▀▄▄▄ ███ ▀▀▄▀█  █ ▄▀██
██▀▄▀▄ ▄▄▀ █ ██ ▀█ ▄█▀  ▄ ▀ █▀▄█▀▀▀ █▀█  ▀▀ ███▄███ █▀ ██
██ ▀▀  ▀▄██  █▀█▀ ▄▀▀▄▀ ▀▀▄ █▀ █  ▀▄ ▀▄ ▀ ▀ ▀▀ ▀▀▄ █▀▀▄██
██▀▄ ▀ ▀▄▄▀▄█▄  ▀█ ▄ ██▀ ▄ ▀█ ██▀█▀  █▄▀▀▄▄▀█  █▄▄▄▀▄████
██▀ ▄▀ ▄▄▄ █ █ █▀█▄▀▄ ▀█ █ ▄▄▄   ▄ ▀█▀▄▄█▀▄ ▀█ ▄▄▄  ▄▄ ██
██▀▀██ █▄█ ▄▄▀█▀█▀  ▄▀ █▀█ █▄█ ▀  ▄▄▄▄█  ▀▀▀▄▄ █▄█ ▀▀ ▀██
██▀▀▀█▄ ▄ ▄█▀  ▄▄█▀▀  ██▀ ▄▄▄▄▄▀▀▀█ ▄▄ ▀██▀ ▀▄▄▄▄    █▀██
██   █▄ ▄█ ▄▄██▄▀▀█▄▄▀   ▄█ ▄██▄  █▀ ▀▄▄▀▀▀ █▀██ █▀▀██▄██
██▄  █▄ ▄▀▄██▀▄▄█  ▄▄▀▄▀█ █▀▀▄█▄ ▄█▄▀   ▀▀█▀▀▀█▄▄ ▀ ▄ ▄██
██   █▄█▄▀▄▄▄█ █▀▄▄▀▄▀▀▀▄█▀█▀▀▄  █▀█▄▄██▀▄▀▀▀▀▀▄▀█ ▀▄█▀██
██▀▀█▀▄▄▄▀█▀ █▄█▀ ▄▀█ █▀ ▀▄█ ▀   ▀▄██▀▄▄▄▀▄▀▀ ▀▀▄  ▄▀▀▄██
███  ▄▄▀▄▀ █▀ █▀▀▄▀  ▄ █▄█▄▄▄   ███▀▄ ▄▄ ▄ █▀ ▄▀█ █▄▀▀▀██
██ ▄█▀▄▀▄  ▄█▄▄  ▀  ▀███▄ ▄▄▀ █ ▀▄█ ▄█▄ █▀█▀▀▀▄█▄█▀▄▄  ██
██▄ ▀▄▄▄▄█ ▄▄▀████▀▄▄▀█▄▄▄▀█▄ █▄▀█ ▄█▄▄█▄ ▀█▄ ▄  ▄▄▀█▀▄██
█████▄██▄█▀ ▄ █   ▄ █▄ ▀█▄ ▄▄▄ ▀▀ █▀▀  ▄▀▄▀▀▀▀ ▄▄▄ ▀▀ ███
██ ▄▄▄▄▄ ██  ▄█▄▄▄▄▀  █ █▀ █▄█ ▀█▀▀ ▄▄   ▄ █▀  █▄█ ▀█▄███
██ █   █ ██ ▄▀ ▄█▀█▄▄▀█ ▄█▄ ▄    ▄▄▀█▀ ▀█▀▄ ▀█▄▄▄ ▄▀█▄▀██
██ █▄▄▄█ ██▀█ ▄▀▀█▄▀ █▀ █▄█ ▀▄▀▀█▀▀▀▀ ▄   ▄▀▀▄▀ ▀▄ ▀▀▄ ██
██▄▄▄▄▄▄▄█▄▄██▄████▄▄▄█▄██▄███▄██▄█▄██▄████▄▄▄▄█▄██▄▄████
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
二维码扫描成功，请授权登录。
扫码登录成功
验证通过
Login successfully! Welcome, 张三!
Your related active passengers:
+------+--------+------+----------------+--------------------+----------+-------------+
| 序号 |  姓名  | 性别 |    证件类型    |       证件号       | 身份类型 |    手机号   |
+------+--------+------+----------------+--------------------+----------+-------------+
|  1   |  张三  |  男  | 中国居民身份证 | **************2333 |   成人   | 18888888888 |
+------+--------+------+----------------+--------------------+----------+-------------+
The passenger results have been stored into 'passengers' list.
## 若使用手机验证码
(12306)>login -m sms -u 18888888888
Input the last 4 digits of your ID card:2333
获取手机验证码成功！
Input your password:
Input verification code:666666
登录成功
验证通过
Login successfully! Welcome, 张三!
+------+--------+------+----------------+--------------------+----------+-------------+
| 序号 |  姓名  | 性别 |    证件类型    |       证件号       | 身份类型 |    手机号   |
+------+--------+------+----------------+--------------------+----------+-------------+
|  1   |  张三  |  男  | 中国居民身份证 | **************2333 |   成人   | 18888888888 |
+------+--------+------+----------------+--------------------+----------+-------------+
The passenger results have been stored into 'passengers' list.
(12306)>search -s 合肥 -e 上海 -d 20211020 -m 15 -M 16
Query below is performed.
+--------+--------+------------+------+--------------+--------------+--------------+
| 出发站 | 到达站 |    日期    | 类型 | 最早发车时间 | 最晚发车时间 | 是否显示售罄 |
+--------+--------+------------+------+--------------+--------------+--------------+
|  合肥  |  上海  | 2021-10-20 |  --  |      15      |      16      |    False     |
+--------+--------+------------+------+--------------+--------------+--------------+
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
|序号| 车次|出发/到达站|   日期   |出发/到达时间| 历时|商务座|特等座|一等座|二等座|高级软卧|软卧|动卧|硬卧|软座|硬座|无座|有票|备注|
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 1  |G7374|  始 合肥  |2021-10-20|    15:05    |02:58|  有  |  --  |  有  |  有  |   --   | -- | -- | -- | -- | -- | 无 | Y  |预订|
|    |     |到 上海虹桥|          |    18:03    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 2  |D3074| 始 合肥南 |2021-10-20|    15:13    |03:12|  --  |  --  | 候补 |  19  |   --   | -- | -- | -- | -- | -- | 无 | Y  |预订|
|    |     |到 上海虹桥|          |    18:25    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 3  |D3074| 始 合肥南 |2021-10-20|    15:13    |03:47|  --  |  --  |  10  |  20  |   --   | -- | -- | -- | -- | -- | 无 | Y  |预订|
|    |     | 到 上海南 |          |    19:00    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 4  |G1958|  始 合肥  |2021-10-20|    15:15    |02:39|  1   |  --  |  8   |  有  |   --   | -- | -- | -- | -- | -- | -- | Y  |预订|
|    |     |到 上海虹桥|          |    17:54    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 5  |G7246| 始 合肥南 |2021-10-20|    15:22    |03:14|  --  |  --  |  有  |  有  |   --   | -- | -- | -- | -- | -- | 无 | Y  |预订|
|    |     |  到 上海  |          |    18:36    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 6  | G678| 始 合肥南 |2021-10-20|    15:28    |02:34| 候补 |  --  |  有  |  有  |   --   | -- | -- | -- | -- | -- | -- | Y  |预订|
|    |     |到 上海虹桥|          |    18:02    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 7  |G7267|始 合肥北城|2021-10-20|    15:48    |03:23|  --  |  --  |  有  |  有  |   --   | -- | -- | -- | -- | -- | 无 | Y  |预订|
|    |     |  到 上海  |          |    19:11    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 8  |G7242| 始 合肥南 |2021-10-20|    15:54    |02:57| 候补 |  --  |  9   |  有  |   --   | -- | -- | -- | -- | -- | 无 | Y  |预订|
|    |     |  到 上海  |          |    18:51    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
The search results have been stored into 'tickets' list.
(12306)>select_ticket 8
Submit ticket info successfully!
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
|序号| 车次|出发/到达站|   日期   |出发/到达时间| 历时|商务座|特等座|一等座|二等座|高级软卧|软卧|动卧|硬卧|软座|硬座|无座|有票|备注|
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
| 1  |G7242| 始 合肥南 |2021-10-20|    15:54    |02:57| 候补 |  --  |  9   |  有  |   --   | -- | -- | -- | -- | -- | 无 | Y  |预订|
|    |     |  到 上海  |          |    18:51    |     |      |      |      |      |        |    |    |    |    |    |    |    |    |
+----+-----+-----------+----------+-------------+-----+------+------+------+------+--------+----+----+----+----+----+----+----+----+
The ticket shown above has been selected successfully.
(12306)>add_order 1
Choose ticket type:
1: 成人
2: 儿童
3: 学生
4: 残军
Press Enter to choose default value '1'

Choose seat type:
1: 二等座
2: 一等座
3: 商务座
4: 硬卧
5: 硬座
6: 软卧
Press Enter to choose default value '1'

Choose your seat:
1: A
2: B
3: C
4: D
5: F
Press Enter to let the system randomly allocate seats for you.
5

+------+--------+--------+--------+----------------+--------------------+-------------+------+
| 序号 |  票种  |  席别  |  姓名  |    证件类型    |      证件号码      |   手机号码  | 选座 |
+------+--------+--------+--------+----------------+--------------------+-------------+------+
|  1   | 成人票 | 二等座 |  张三  | 中国居民身份证 | **************2333 | 18888888888 |  F   |
+------+--------+--------+--------+----------------+--------------------+-------------+------+
Order info shown above has been added Successfully.
(12306)>queue_count
查询成功,本次列车二等座余票 467 张, 无座余票 0 张
(12306)>confirm
Congratulations!!!Please go to 12306 APP and pay for your tickets!
+------+-------+-------------+------------------+--------+----------------+--------------------+----------+--------+------+--------+-------+
| 序号 |  车次 | 出发/到达站 |     出发时间     |  姓名  |    证件类型    |      证件号码      | 车票类型 |  席位  | 车厢 | 座位号 |  价格 |
+------+-------+-------------+------------------+--------+----------------+--------------------+----------+--------+------+--------+-------+
|  0   | G7242 |  始 合肥南  | 2021-10-20 15:54 | 张三  | 中国居民身份证 | **************2333 |  成人票  | 二等座 |  06  | 03F号  | 210.0 |
|      |       |   到 上海   |                  |        |                |                    |          |        |      |        |       |
+------+-------+-------------+------------------+--------+----------------+--------------------+----------+--------+------+--------+-------+
```