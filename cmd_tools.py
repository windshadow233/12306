import cmd2
import sys
from prettytable import PrettyTable, ALL
import time
from retry import retry
from bot.ticket_bot import RailWayTicketBot


class TicketBotShell(cmd2.Cmd):
    intro = 'Welcome to the 12306 ticket bot shell. Type help or ? to list commands.\n' \
            'You\'re required a fast and stable network environment to use this shell.\n' \
            'BTW, you\'d better use this shell in full screen mode.'
    prompt = '(12306)>'
    bot = RailWayTicketBot()
    tickets = []
    passengers = []
    orders = []
    selected_ticket = None
    last_queue_args = None
    passenger_strs = []
    passenger_old_strs = []
    need_queue = False

    search_parser = cmd2.Cmd2ArgumentParser(description='Search for tickets information')
    search_parser.add_argument('-s', '--start', type=str, required=True, help='Start Station')
    search_parser.add_argument('-e', '--end', type=str, required=True, help='Arrive Station')
    search_parser.add_argument('-d', '--date', type=str,
                               help='Date (format: %%Y%%m%%d, eg: 20210512, default: today)', default=None)
    search_parser.add_argument('-t', '--type', type=str.upper, help='Type of Train (The first letter of train number)',
                               choices=['G', 'D', 'K', 'T', 'Z'], default=None)
    search_parser.add_argument('-m', '--min_start_hour', type=int, choices=range(24), default=0,
                               help='The minimum start hour (0~23)')
    search_parser.add_argument('-M', '--max_start_hour', type=int, choices=range(25), default=24,
                               help='The maximum start hour (0~24)')
    search_parser.add_argument('-a', '--all', action='store_true',
                               help='If set, tickets which have been sold out will also be shown.')

    @cmd2.with_argparser(search_parser)
    def do_search(self, args):
        print("Query below is performed.")
        if args.date is None:
            args.date = time.strftime("%Y-%m-%d")
        else:
            date = time.strptime(args.date, "%Y%m%d")
            args.date = time.strftime("%Y-%m-%d", date)
        self.print_query(args)
        self.tickets = self.bot.get_ticket_info(args.start, args.end, args.date, args.type,
                                                args.all, args.min_start_hour, args.max_start_hour)
        if self.tickets:
            self.bot.print_ticket_info(self.tickets)
        else:
            print('No tickets found, change the stations name, date or other parameters and try again.')
        print('The search results have been stored into \'tickets\' list.')
        self.last_queue_args = args

    get_passenger_parser = cmd2.Cmd2ArgumentParser(description='Get your related passengers if you\'re login.')
    get_passenger_parser.add_argument('-a', '--all', action='store_true',
                                      help='If set, show all non-active passengers.')

    def print_query(self, args):
        query_table = PrettyTable(['出发站', '到达站', '日期', '类型', '最早发车时间', '最晚发车时间', '是否显示售罄'], hrules=ALL)
        query_table.add_row([args.start, args.end, args.date,
                             args.type or '--', args.min_start_hour, args.max_start_hour, args.all])
        print(query_table)

    def do_update_tickets(self, args):
        """Update tickets info by latest query."""
        if self.last_queue_args is None:
            print('No queue to update.')
            return
        args = self.last_queue_args
        print('Update query below:')
        self.print_query(args)
        self.tickets = self.bot.get_ticket_info(args.start, args.end, args.date, args.type,
                                                args.all, args.min_start_hour, args.max_start_hour)
        if not self.tickets:
            print('No tickets found, change the stations name, date or other parameters and try again.')
        print('The results of the above query has been updated successfully.')
        if self.selected_ticket is None:
            return
        train_id = self.selected_ticket["train_id"]
        for ticket in self.tickets:
            if ticket["train_id"] == train_id and ticket["has_ticket"] == 'Y':
                break
        else:
            print(f"The selected train ID: {train_id} has been sold out!")
            self.selected_ticket = None
            return
        self.select_ticket(ticket)

    @cmd2.with_argparser(get_passenger_parser)
    def do_get_passengers(self, args):
        if not self.bot.check_login():
            print('Please get login first.')
            return
        else:
            self.passengers = self.bot.get_passengers(args.all)
        self.bot.print_passengers(self.passengers)
        print('The passenger results have been stored into \'passengers\' list.')

    show_parser = cmd2.Cmd2ArgumentParser(description='Show something')
    show_parser.add_argument('item', type=str, choices=['tickets', 'passengers', 'orders', 'selected_ticket'])

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
        elif args.item == 'orders':
            if not self.orders:
                print('There is no order_info saved in cache. Use cmd \'add_order\' to add.')
                return
            self.bot.print_orders(self.orders)
        elif args.item == 'selected_ticket':
            if not self.selected_ticket:
                print('No ticket selected! Please select one first!')
                return
            self.bot.print_ticket_info([self.selected_ticket])

    login_parser = cmd2.Cmd2ArgumentParser(description='Get login')
    login_parser.add_argument('-m', '--method', type=str,
                              help='Method to Login.\n'
                              'qr: to login with QR code\n'
                              'sms: to login with sms code (Usage count is limited in a day)',
                              choices=['qr', 'sms'], default='qr')
    login_parser.add_argument('-u', '--user', type=str, help='User Name (Your Phone Number)')

    @retry(tries=10, delay=0.5)
    @cmd2.with_argparser(login_parser)
    def do_login(self, args):
        """Get login."""
        if args.method == 'sms':
            if not args.user:
                print('未提供手机号!(-u)')
                return
            r = self.bot.sms_login(args.user)
        else:
            r = self.bot.qr_login()
        if r:
            print('Your related active passengers:')
            self.do_get_passengers("")

    clear_parser = cmd2.Cmd2ArgumentParser(description="Clear some list attributes.")
    clear_parser.add_argument("item", type=str, choices=['passengers', 'tickets', 'orders', 'selected_ticket'])

    @cmd2.with_argparser(clear_parser)
    def do_clear(self, args):
        if isinstance(self.__getattribute__(args.item), list):
            self.__getattribute__(args.item).clear()
            if args.item == 'orders':
                self.passenger_strs.clear()
                self.passenger_old_strs.clear()
        else:
            self.__setattr__(args.item, None)

    def do_logout(self, args):
        """Get logout."""
        self.bot.logout()
        self.passengers.clear()
        self.selected_ticket = None
        self.orders.clear()
        self.passenger_strs.clear()
        self.passenger_old_strs.clear()
        self.need_queue = True

    @retry(tries=10, delay=0.5)
    def do_is_login(self, args):
        """Check whether you're login or not."""
        print(self.bot.check_login())

    select_ticket_parser = cmd2.Cmd2ArgumentParser(description='Choose a ticket to buy.')
    select_ticket_parser.add_argument('id', type=int, help='Ticket ID in \'tickets\' list.')

    def select_ticket(self, ticket):
        submit_success, r = self.bot.submit_order_request(ticket)
        if submit_success:
            print('Submit ticket info successfully!')
        if not submit_success:
            if r is not None:
                print(r['messages'][0])
                if "车票信息已过期" in r['messages'][0]:
                    print('Use \'update_tickets\' cmd and retry.')
            return
        self.bot.get_init_info()
        self.selected_ticket = ticket
        self.bot.print_ticket_info([ticket])
        self.need_queue = True
        print('The ticket shown above has been selected successfully.')

    @cmd2.with_argparser(select_ticket_parser)
    def do_select_ticket(self, args):
        if not self.tickets:
            print('No tickets stored. Use \'search\' cmd to fetch.')
            return
        ticket_id = args.id
        if not 1 <= ticket_id <= len(self.tickets):
            print(f'Ticket ID out of range! Select \'{ticket_id}\', but the range is 1 ~ {len(self.tickets)}.')
            return
        has_ticket = self.tickets[ticket_id - 1]['has_ticket'] == 'Y'
        if not has_ticket:
            print('The ticket you select has been sold out!')
            return
        self.select_ticket(self.tickets[ticket_id - 1])

    add_order_parser = cmd2.Cmd2ArgumentParser(description="Add a piece of order.")
    add_order_parser.add_argument('id', type=int,
                                  help='Passenger ID in \'passengers\' list.')

    @cmd2.with_argparser(add_order_parser)
    def do_add_order(self, args):
        if not self.passengers:
            print('No passengers stored. Use \'get_passengers\' cmd to fetch.')
            return
        passenger_id = args.id
        if not 1 <= passenger_id <= len(self.passengers):
            print(f'Passenger ID out of range! Choose {passenger_id}, but the range is 1 ~ {len(self.passengers)}.')
            return
        is_active = self.passengers[passenger_id - 1]['if_receive']
        if is_active != 'Y':
            print('The chosen passenger is not active!')
            return
        for order in self.orders:
            if passenger_id == order.get('id'):
                print('The chosen passenger is already in order list.')
                return
        passenger = self.passengers[passenger_id - 1]
        while 1:
            ticket_type = input('Choose ticket type:\n'
                                '1: 成人\n'
                                '2: 儿童\n'
                                '3: 学生\n'
                                '4: 残军\n'
                                'Press Enter to choose default value \'1\'\n') or '1'
            if ticket_type.isdigit() and int(ticket_type) in range(1, 5):
                if ticket_type != '1':
                    ok = input('Your choice is not adult ticket.\n'
                               'Please ensure that the identity of chosen passenger matches what you choose, '
                               'or you may get failed.\nIf you want to choose again, type \'N\'.\n').upper() or 'Y'
                    if ok == 'Y':
                        break
                else:
                    break
                continue
            print('Invalid input!')
        print('')
        seat_types = self.bot.seat_type_choice[ticket_type]
        msg = 'Choose seat type:\n'
        for i, t in enumerate(seat_types, 1):
            msg += f'{i}: {self.bot.seat_type_dict[t]}\n'
        msg += 'Press Enter to choose default value \'1\'\n'
        while 1:
            seat_type = input(msg) or '1'
            if seat_type.isdigit() and 0 < int(seat_type) <= len(seat_types):
                break
            print('Invalid input!')
        seat_type = seat_types[int(seat_type) - 1]
        print('')
        while 1:
            valids = self.bot.seat_number_choice.get(seat_type, [])
            if not valids:
                print('Choosing seat is not available for your seat type!')
                choose_seat = ''
            else:
                msg = 'Choose your seat:\n'
                for i, valid in enumerate(valids, 1):
                    msg += f'{i}: {valid}\n'
                msg += 'Press Enter to let the system randomly allocate seats for you.\n'
                choose_seat = input(msg) or ''
            if choose_seat == '':
                break
            if choose_seat.isdigit() and 0 < int(choose_seat) <= len(valids):
                choose_seat = valids[int(choose_seat) - 1]
                break
            print('Invalid input!')
        print('')
        added = {
            'id': passenger_id,
            "passenger": passenger,
            "seat_type": seat_type,
            "ticket_type": ticket_type,
            "choose_seat": choose_seat
        }
        self.orders.append(added)
        self.passenger_strs.append(self.bot.generate_passenger_ticket_str(passenger, seat_type, ticket_type))
        self.passenger_old_strs.append(self.bot.generate_old_passenger_str(passenger))
        self.bot.print_orders([added])
        self.need_queue = True
        print('Order info shown above has been added Successfully.')

    del_order_parser = cmd2.Cmd2ArgumentParser(description='Remove a piece of order.')
    del_order_parser.add_argument('id', type=int, help='Order ID in \'order\' list.')

    @cmd2.with_argparser(del_order_parser)
    def do_rm_order(self, args):
        if not self.orders:
            print('No order stored. Use \'add_order\' cmd to add.')
            return
        order_id = args.id
        if not 1 <= order_id <= len(self.orders):
            print(f'Order ID out of range! Choose {order_id}, but the range is 1 ~ {len(self.orders)}.')
            return
        self.bot.print_orders([self.orders[order_id - 1]])
        self.orders.pop(order_id - 1)
        self.passenger_strs.pop(order_id - 1)
        self.passenger_old_strs.pop(order_id - 1)
        self.need_queue = True
        print('The order shown above has been removed successfully.')

    @retry(tries=10, delay=0.5)
    def do_queue_count(self, args):
        """Query for the count of tickets left."""
        if self.selected_ticket is None or not self.orders:
            print('Ticket or order information is not completed.')
            return
        status, r = self.bot.check_order_info(self.passenger_strs, self.passenger_old_strs)
        if not status:
            print(r['messages'][0])
            return
        seat_type = self.orders[0]['seat_type']
        status, r = self.bot.get_queue_count(seat_type)
        if not status:
            print(r['messages'][0])
            return
        tickets_left = r['data']['ticket'].split(',')
        if len(tickets_left) == 2:
            print(f'查询成功,本次列车{self.bot.seat_type_dict[seat_type]}余票 {tickets_left[0]} 张, 无座余票 {tickets_left[1]} 张')
        else:
            print(f'查询成功,本次列车{self.bot.seat_type_dict[seat_type]}余票 {tickets_left[0]} 张')
        self.need_queue = False

    @retry(tries=10)
    def do_confirm(self, args):
        """抢票!!!"""
        if self.selected_ticket is None or not self.orders:
            print('Ticket or order information is not completed.')
            return
        if self.need_queue:
            print('Please queue for count first!')
            return
        seats = ''
        for i, order in enumerate(self.orders, 1):
            seat = order['choose_seat']
            if seat:
                seats += f'{i}{seat}'
        success, r = self.bot.confirm_single_for_queue(self.passenger_strs, self.passenger_old_strs, seats)
        if success:
            print('Congratulations!!!Please go to 12306 APP and pay for your tickets!')
            self.bot.print_ticket_info([self.selected_ticket])
        else:
            raise Exception

    def do_bye(self, args):
        """Say bye to the shell."""
        print('Thank you for using 12306 ticket bot shell.\nBye~')
        return True

    do_quit = do_bye


if __name__ == "__main__":
    sys.exit(TicketBotShell().cmdloop())
