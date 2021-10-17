# 一个十分简陋的12306命令行工具

此项目仅供学习、娱乐

若出现网络问题或一些奇怪的报错, 大概率是12306自身的问题, 重新进入程序或多次重试一般即可成功, 若仍失败, 可能网络环境有问题, 考虑重启、重连WiFi等。

若遇到扫码登录无反应、系统错误或授权失败等情况, 请使用组合键Ctrl + C断开命令, 并重新使用```login```命令。

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
- [ ] 候补（不打算搞, 感觉都候补了也没必要用脚本）


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
## 命令详解

1. 登录

```login```

|子命令|说明|参数|
|:---:|:---:|:---:|
|qr|扫二维码登录|无|
|sms|手机短信验证码登录|-u, --user 手机号|
|check|检查登录状态|无|
2. 登出

```logout```

3. 车票

```ticket```

|子命令|说明|参数|
|:---:|:---:|:---:|
|search|查询车票信息|-s, --start 出发站<br>-e, --end 到达站<br>-d, --date 出发日期<br>-t, --type 列车类型<br>-m, --min_start_hour 最早出发时间<br>-M, --max_start_hour 最晚出发时间<br>-a, --all 标志参数, 不忽略售罄车票|
|update|根据上一条搜索记录<br>更新车票信息|无|
|select|选择车票|id 位置参数, 车票对应的ID, 通过子命令show可见|
|show|打印存储的车票信息|无<br>拥有子命令selected, 打印选中的车票信息|
|clear|清除车票信息|无|
4. 乘车人

```passenger```

|子命令|说明|参数|
|:---:|:---:|:---:|
|get|获取相关乘车人信息|-a, --all 标志参数, 不忽略未核验乘车人|
|show|打印存储的乘车人信息|无|
|clear|清除乘车人信息|无|

5. 订单

```order```

|子命令|说明|参数|
|:---:|:---:|:---:|
|add|添加一条订单|id 位置参数, 乘车人对应的ID, 通过命令passenger show可见|
|rm|删除一条订单|id 位置参数, 订单对应的ID, 通过子命令show可见|
|clear|清空订单|无|
|show|打印订单信息|无|
|queue|余票查询|无|
|confirm|提交订单|无|

6. 自动订票

```auto_run```

|参数|说明|
|:---:|:---:|
|-f, --yml_file|一个配置好的文件, 以.yml为扩展名, 模板见config.yml<br>如不提供此参数, 默认为config.yml|



7. 退出程序

你当然可以粗暴地杀掉进程,但仍建议使用:

```bye```

温柔地与它道别

---
另有一些其他自带的命令, 不过应该用不上。

详情以及命令的参数请使用```help```或```-h```查看。
## 手动订票流程

1. ```login```(登录)
2. ```ticket search```(查票)
3. ```ticket select```(选票)
4. ```order add```(添加订单)
5. ```order queue```(余票查询)
6. ```order confirm```(提交订单)

## 自动订票流程
1. 根据订票需求, 按照给定模板提前编辑好yml文件, 放置于工作目录下
2. 在工作目录下运行程序
3. 运行 ```auto_run```命令, 即可全自动订票
