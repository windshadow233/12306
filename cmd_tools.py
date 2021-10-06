import cmd2
import sys
from bot.ticket_bot import RailWayTicketBot


class TicketBotShell(cmd2.Cmd):
    intro = 'Welcome to the bot ticket bot shell. Type help or ? to list commands.\n' \
            'You\'re required a stable network environment to use this shell.'
    prompt = '(12306)>'
    bot = RailWayTicketBot()
    tickets = []
    passengers = []
    order_info = []
    chosen_ticket = None

    search_parser = cmd2.Cmd2ArgumentParser(description='Search for tickets information')
    search_parser.add_argument('-s', '--start', type=str, help='Start Station')
    search_parser.add_argument('-e', '--end', type=str, help='Arrive Station')
    search_parser.add_argument('-d', '--date', type=str,
                               help='Date (format: %%Y%%m%%d, eg: 20210512, default: today)', default=None)
    search_parser.add_argument('-t', '--type', type=str.upper, help='Type of Train (The first letter of train number)',
                               choices=['G', 'D', 'K', 'T', 'Z'], default=None)
    search_parser.add_argument('-a', '--all', action='store_true',
                               help='If set, tickets which have been sold out will also be shown.')
    search_parser.add_argument('-m', '--min_start_hour', type=int, choices=range(24), default=0,
                               help='The minimum start hour (0~23)')
    search_parser.add_argument('-M', '--max_start_hour', type=int, choices=range(25), default=24,
                               help='The maximum start hour (0~24)')

    @cmd2.with_argparser(search_parser)
    def do_search(self, args):
        if args.date is not None:
            args.date = f'{args.date[:4]}-{args.date[4: 6]}-{args.date[6:]}'
        self.tickets = self.bot.get_ticket_info(args.start, args.end, args.date, args.type,
                                                args.all, args.min_start_hour, args.max_start_hour)
        if self.tickets:
            self.bot.print_ticket_info(self.tickets)
        else:
            print('No tickets found, change the stations name, date or other parameters and try again.')
        print('The search results have been stored into \'tickets\' list.')

    get_passenger_parser = cmd2.Cmd2ArgumentParser(description='Get your related passengers if you\'re login.')
    get_passenger_parser.add_argument('-a', '--all', action='store_true',
                                      help='If set, show all non-active passengers.')

    @cmd2.with_argparser(get_passenger_parser)
    def do_get_passengers(self, args):
        if not self.bot.check_login():
            print('Please get login first.')
            return
        else:
            self.passengers = self.bot.get_passengers(args.all)
        self.bot.print_passengers(self.passengers)
        print('The search results have been stored into \'passengers\' list.')

    show_parser = cmd2.Cmd2ArgumentParser(description='Show something')
    show_parser.add_argument('item', type=str, choices=['tickets', 'passengers', 'order_info', 'chosen_ticket'])

    @cmd2.with_argparser(show_parser)
    def do_show(self, args):
        if args.item == 'tickets':
            if not self.tickets:
                print('There is no tickets saved in cache. Use cmd \'search\' to fetch.')
                return
            self.bot.print_ticket_info(self.tickets)
        elif args.item == 'passengers':
            if not self.passengers:
                print('There is no passengers saved in cache. Use cmd \'get_passengers\' to fetch.')
                return
            self.bot.print_passengers(self.passengers)
        elif args.item == 'order_info':
            if not self.order_info:
                print('There is no order_info saved in cache. Use cmd \'add_order\' to add.')
                return
            self.bot.print_order_info(self.order_info)
        elif args.item == 'chosen_ticket':
            if not self.chosen_ticket:
                print('No chosen ticket! Please choose one first!')
                return
            self.bot.print_ticket_info([self.chosen_ticket])


    # login_parser = cmd2.Cmd2ArgumentParser(description='Get login')
    # login_parser.add_argument('-m', '--method', type=str,
    #                           help='Method to Login.\n'
    #                           'qr: to login with QR code\n'
    #                           'sms: to login with sms code(Usage count is limited in a day)',
    #                           choices=['qr', 'sms'], default='qr')
    # login_parser.add_argument('-u', '--user', type=str, help='User Name (Your Phone Number)')
    # login_parser.add_argument('-p', '--password', type=str, help='Your Password')
    # login_parser.add_argument('-c', '--cast_num', type=str, help='Last 4 digits of Your ID Card')

    # @cmd2.with_argparser(login_parser)
    def do_login(self, args):
        """Get login."""
        # if args.method == 'sms':
        #     if not args.user:
        #         print('未提供手机号!(-u)')
        #         exit(-1)
        #     if not args.password:
        #         print('未提供密码!(-p)')
        #         exit(-1)
        #     if not args.cast_num:
        #         print('未提供身份证后四位!(-c)')
        #         exit(-1)
        #     self.bot.sms_login(args.user, args.password, args.cast_num)
        # else:
        self.bot.qr_login()

    clear_parser = cmd2.Cmd2ArgumentParser(description="Clear some list attributes.")
    clear_parser.add_argument("item", type=str, choices=['passengers', 'tickets', 'order_info', 'chosen_ticket'])

    @cmd2.with_argparser(clear_parser)
    def do_clear(self, args):
        if isinstance(self.__getattribute__(args.item), list):
            self.__getattribute__(args.item).clear()
        else:
            self.__setattr__(args.item, None)

    def do_logout(self, args):
        """Get logout."""
        self.bot.logout()
        self.passengers.clear()
        self.order_info.clear()

    def do_is_login(self, args):
        """Check whether you're login or not."""
        print(self.bot.check_login())

    choose_ticket_parser = cmd2.Cmd2ArgumentParser(description='Choose a ticket to buy.')
    choose_ticket_parser.add_argument('id', type=int, help='Ticket ID in \'tickets\' list.')

    @cmd2.with_argparser(choose_ticket_parser)
    def do_choose_ticket(self, args):
        if not self.tickets:
            print('No tickets stored. Use \'search\' cmd to fetch.')
            return
        ticket_id = args.id
        if not 1 <= ticket_id <= len(self.tickets):
            print(f'Ticket ID out of range! Chosen {ticket_id}, but the range is 1 ~ {len(self.tickets)}.')
            return
        has_ticket = self.tickets[ticket_id - 1]['has_ticket'] == 'Y'
        if not has_ticket:
            print('The ticket you choose has been sold out!')
            return
        self.chosen_ticket = self.tickets[ticket_id - 1]
        self.bot.print_ticket_info([self.chosen_ticket])
        print('The ticket shown above is chosen successfully.')

    add_order_parser = cmd2.Cmd2ArgumentParser(description="Add a piece of order.")
    add_order_parser.add_argument('-p', '--passenger', type=int, help='Passenger ID in \'passengers\' list.')
    add_order_parser.add_argument('-s', '--seat_type', type=str.upper, choices=['M', 'O', 'P', '9'], default='O',
                                  help='Seat Type\nM: 一等座\nO: 二等座\nP: 特等座\n9: 商务座')
    add_order_parser.add_argument('-t', '--ticket_type', type=int, choices=range(1, 5), default=1,
                                  help='Ticket Type\n1: 成人\n2: 儿童\n3: 学生\n4: 残军')

    @cmd2.with_argparser(add_order_parser)
    def do_add_order(self, args):
        if not self.passengers:
            print('No passengers stored. Use \'get_passengers\' cmd to fetch.')
            return
        passenger_id = args.passenger
        if not 1 <= passenger_id <= len(self.passengers):
            print(f'Passenger ID out of range! Choose {passenger_id}, but the range is 1 ~ {len(self.passengers)}.')
            return
        is_active = self.passengers[passenger_id - 1]['is_active']
        if is_active != 'Y':
            print('Chosen passenger not active!')
            return
        all_passenger_id = [order.get('id') for order in self.order_info]
        if passenger_id in all_passenger_id:
            print('Chosen passenger already in order list.')
            return
        added = {
            'id': passenger_id,
            "passenger": self.passengers[passenger_id - 1],
            "seat_type": args.seat_type,
            "ticket_type": str(args.ticket_type)
        }
        self.order_info.append(added)
        self.bot.print_order_info([added])
        print('Order info shown above added Successfully.')

    del_order_parser = cmd2.Cmd2ArgumentParser(description='Remove a piece of order.')
    del_order_parser.add_argument('id', type=int, help='Order ID in \'order\' list.')

    @cmd2.with_argparser(del_order_parser)
    def do_rm_order(self, args):
        if not self.order_info:
            print('No order stored. Use \'add_order\' cmd to add.')
            return
        order_id = args.id
        if not 1 <= order_id <= len(self.order_info):
            print(f'Order ID out of range! Choose {order_id}, but the range is 1 ~ {len(self.order_info)}.')
            return
        self.bot.print_order_info([self.order_info[order_id - 1]])
        self.order_info.pop(order_id - 1)
        print('The order shown above is remove successfully.')

    def do_buy(self, args):
        if self.chosen_ticket is None or not self.order_info:
            print('Ticket and order information is not completed.')
            return
        submit_success = self.bot.submit_order_request(self.chosen_ticket)
        if not submit_success:
            return
        r = self.bot.check_order_info(self.order_info).json()
        if not r['status']:
            print(r['messages'][0])
            return
        seat_type = self.order_info[0]['seat_type']
        r = self.bot.get_queue_count(seat_type).json()
        if not r['status']:
            print(r['messages'][0])
            return
        tickets_left = r['data']['ticket'].split(',')
        if len(tickets_left) == 2:
            print(f'查询成功,本次列车{self.bot.code2seat[seat_type]}余票 {tickets_left[0]} 张, 无座余票 {tickets_left[1]} 张')
        else:
            print(f'查询成功,本次列车{self.bot.code2seat[seat_type]}余票 {tickets_left[0]} 张')

    def do_bye(self, args):
        """Say bye to the shell."""
        print('Thank you for using bot ticket bot shell.\nBye~')
        return True

    do_quit = do_bye


if __name__ == "__main__":
    sys.exit(TicketBotShell().cmdloop())
