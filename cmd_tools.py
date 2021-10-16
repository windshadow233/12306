import argparse
import cmd2
import yaml
import os
from bot.ticket_bot import RailWayTicketBot
from cmds import TicketsCmd, LoginCmd, PassengersCmd, OrderCmd


class TicketBotShell(cmd2.Cmd, TicketsCmd, LoginCmd, PassengersCmd, OrderCmd):
    intro = 'Welcome to the 12306 ticket bot shell. Type help or ? to list commands.\n' \
            'You\'re required a fast and stable network environment to use this shell.\n' \
            'BTW, you\'d better use this shell in full screen mode.'
    prompt = '(12306)>'
    bot = RailWayTicketBot()

    def __init__(self):
        super(TicketBotShell, self).__init__()
        TicketsCmd.__init__(self)
        LoginCmd.__init__(self)
        PassengersCmd.__init__(self)
        OrderCmd.__init__(self)
        self.need_queue = False

    show_parser = cmd2.Cmd2ArgumentParser(description='Show something')
    show_parser.add_argument('item', type=str,
                             choices=['tickets', 'passengers', 'orders', 'selected_ticket'])

    @cmd2.with_argparser(show_parser)
    def do_show(self, args):
        if args.item == 'tickets':
            if not self.tickets:
                print('No tickets saved in cache! Use \'search\' cmd to fetch.')
                return
            self.bot.print_ticket_info(self.tickets)
        elif args.item == 'passengers':
            if not self.passengers:
                print('No passengers saved in cache! Use \'get_passengers\' cmd to fetch.')
                return
            self.bot.print_passengers(self.passengers)
        elif args.item == 'orders':
            if not self.orders:
                print('No order_info saved in cache! Use \'add_order\' cmd to add.')
                return
            self.bot.print_orders(self.orders)
        elif args.item == 'selected_ticket':
            if not self.selected_ticket:
                print('No ticket selected! Use \'select_ticket\' cmd to select one.')
                return
            self.bot.print_ticket_info([self.selected_ticket])

    clear_parser = cmd2.Cmd2ArgumentParser(description="Clear something")
    clear_parser.add_argument("item", type=str,
                              choices=['passengers', 'tickets', 'orders', 'selected_ticket'])

    @cmd2.with_argparser(clear_parser)
    def do_clear(self, args):
        if isinstance(self.__getattribute__(args.item), list):
            self.__getattribute__(args.item).clear()
            if args.item == 'orders':
                self.__getattribute__('passenger_strs').clear()
                self.__getattribute__('passenger_old_strs').clear()
        else:
            self.__setattr__(args.item, None)

    auto_run_parser = cmd2.Cmd2ArgumentParser('Auto run with a yaml file.')
    auto_run_parser.add_argument('-f', '--yml_file', type=argparse.FileType('r', encoding='utf-8'),
                                 default="config.yml",
                                 help='A configured yaml file, ending with \'.yml\'. Use \'config.yml\' by default.')

    @cmd2.with_argparser(auto_run_parser)
    def do_auto_run(self, args):
        if not self.bot.check_user()[0]:
            print('Please login first.')
            self.do_login("")
        yml_file = args.yml_file
        print(f'Read configuration from {yml_file.name}...')
        data = yaml.safe_load(yml_file.read())
        self.__init__()
        train_info = data['TRAIN']
        passengers = data['PASSENGERS']
        time_mode = train_info['MODE']  # 车票时间顺延模式
        if time_mode not in ['both', 'earlier', 'later']:
            print('TRAIN.MODE is invalid. Valid values: both, earlier, later.')
            return
        from_station_name = train_info['FROM']
        to_station_name = train_info['TO']
        train_type = train_info['TRAIN_TYPE']
        date = train_info['DATE'].strftime('%Y-%m-%d')
        h, m = train_info['TIME'] // 60, train_info['TIME'] % 60
        min_start_hour = train_info['MIN_START_HOUR']
        max_start_hour = train_info['MAX_START_HOUR']
        if h < min_start_hour or h >= max_start_hour:
            print('Expected start time is not between your searching time range.')
            return
        passengers = {p['NAME']: p for p in passengers}
        self.passengers = self.bot.get_passengers()
        names = [p['passenger_name'] for p in self.passengers]
        for name, passenger_info in passengers.items():
            """先生成乘客订单列表"""
            if name not in names:
                continue
            passenger = self.passengers[names.index(name)]
            seat_type = self.bot.seat_type_to_code[passenger_info['SEAT_TYPE']]
            ticket_type = self.bot.ticket_type_to_code[passenger_info['TICKET_TYPE']]
            if seat_type not in self.bot.seat_type_choice[ticket_type]:
                print(f'Seat type is not available for your selected ticket type. '
                      f'Please check the order info of \'{name}\'.')
                return
            added = {
                "passenger": passenger,
                "seat_type": seat_type,
                "ticket_type": ticket_type,
                "choose_seat": passenger_info['SEAT'] or ""
            }
            self.orders.append(added)
            self.__getattribute__('passenger_strs').append(
                self.bot.generate_passenger_ticket_str(passenger, seat_type, ticket_type))
            self.__getattribute__('passenger_old_strs').append(self.bot.generate_old_passenger_str(passenger))
        # 查票
        self.tickets = self.bot.get_ticket_info(from_station_name, to_station_name,
                                                date, train_type, False,
                                                min_start_hour, max_start_hour)
        fully_match_from = train_info['FULLY_MATCH_FROM']  # 是否完全匹配出发站名
        fully_match_to = train_info['FULLY_MATCH_TO']  # 是否完全匹配到达站名
        if fully_match_from:
            def filter_from_station(ticket, from_):
                return ticket['from_station_name'] == from_

            self.tickets = list(filter(lambda x: filter_from_station(x, from_station_name), self.tickets))
        if fully_match_to:
            def filter_to_station(ticket, to_):
                return ticket['to_station_name'] == to_

            self.tickets = list(filter(lambda x: filter_to_station(x, to_station_name), self.tickets))
        if time_mode == 'both':
            # 按与期望发车时间的时间差从小到大排序
            def sort_ticket(ticket, t):
                start_h, start_m = ticket['start_time'].split(':')
                return abs(int(start_h) * 60 + int(start_m) - t)

            self.tickets.sort(key=lambda x: sort_ticket(x, train_info['TIME']))
        else:
            def filter_time(ticket, t, cmp_fcn):
                start_h, start_m = ticket['start_time'].split(':')
                return cmp_fcn(int(start_h) * 60 + int(start_m), t)

            if time_mode == 'earlier':
                # 过滤晚于期望发车时间的车次
                self.tickets = list(filter(lambda x: filter_time(x, train_info['TIME'], int.__le__), self.tickets))
            elif time_mode == 'later':
                # 过滤早于期望发车时间的车次
                self.tickets = list(filter(lambda x: filter_time(x, train_info['TIME'], int.__ge__), self.tickets))
        # 记录下查询参数，便于update
        self.last_queue_args = {
            "start": from_station_name,
            "end": to_station_name,
            "date": date,
            "type": train_type,
            "all": False,
            "min_start_hour": min_start_hour,
            "max_start_hour": max_start_hour
        }
        if not self.tickets:
            print('No tickets found.')
            return
        i = 0
        seat_type = self.orders[0]['seat_type']

        def update():
            """用于更新车票"""
            self.tickets = self.bot.get_ticket_info(from_station_name, to_station_name,
                                                    date, train_type, False,
                                                    min_start_hour, max_start_hour)
            if fully_match_from:
                self.tickets = list(filter(lambda x: filter_from_station(x, from_station_name), self.tickets))
            if fully_match_to:
                self.tickets = list(filter(lambda x: filter_to_station(x, to_station_name), self.tickets))
            if time_mode == 'earlier':
                self.tickets = list(filter(lambda x: filter_time(x, train_info['TIME'], int.__le__), self.tickets))
            elif time_mode == 'later':
                self.tickets = list(filter(lambda x: filter_time(x, train_info['TIME'], int.__ge__), self.tickets))
            else:
                self.tickets.sort(key=lambda x: sort_ticket(x, train_info['TIME']))

        while 1:
            if i >= len(self.tickets):
                print('No tickets available. Retrying...')
                update()
                if not self.tickets:
                    print('No tickets found.')
                    return
                i = 0
            success = self.select_ticket(self.tickets[i])
            if success == -1:  # 非可订票时间段
                return
            if success == 0:  # 车票信息过期
                update()
                if not self.tickets:
                    print('No tickets found.')
                    return
                self.select_ticket(self.tickets[i])
            if self.selected_ticket is None:  # 票无了
                i += 1
                continue
            status, r = self.bot.check_order_info(self.__getattribute__('passenger_strs'),
                                                  self.__getattribute__('passenger_old_strs'))
            if not status:
                print(r['messages'][0])
                i += 1
                continue
            status, r = self.bot.get_queue_count(seat_type)
            if not status:
                print(r['messages'][0])
                i += 1
                continue
            else:
                tickets_left = r['data']['ticket'].split(',')
                if len(tickets_left) == 2:
                    print(
                        f'查询成功,本次列车{self.bot.seat_type_dict[seat_type]}余票 {tickets_left[0]} 张, 无座余票 {tickets_left[1]} 张')
                else:
                    print(f'查询成功,本次列车{self.bot.seat_type_dict[seat_type]}余票 {tickets_left[0]} 张')
                self.need_queue = False
                break
        self.do_confirm("")

    def do_logout(self, args):
        """Get logout"""
        self.bot.logout()
        self.__init__()

    def do_bye(self, args):
        """Say bye to the shell"""
        print('Thank you for using 12306 ticket bot shell.\nBye~')
        return True

    do_quit = do_bye


if __name__ == "__main__":
    print('Initializing...')
    TicketBotShell().cmdloop()
    input('Press Enter to exit.')
