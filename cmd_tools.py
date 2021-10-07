import cmd2
import sys
from prettytable import PrettyTable, ALL
import time
from bot.ticket_bot import RailWayTicketBot


class TicketBotShell(cmd2.Cmd):
    intro = 'Welcome to the 12306 ticket bot shell. Type help or ? to list commands.\n' \
            'You\'re required a stable network environment to use this shell.'
    prompt = '(12306)>'
    bot = RailWayTicketBot()
    tickets = []
    passengers = []
    orders = []
    chosen_ticket = None
    last_queue_args = None

    search_parser = cmd2.Cmd2ArgumentParser(description='Search for tickets information')
    search_parser.add_argument('-s', '--start', type=str, help='Start Station')
    search_parser.add_argument('-e', '--end', type=str, help='Arrive Station')
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
        if args.date is not None:
            args.date = f'{args.date[:4]}-{args.date[4: 6]}-{args.date[6:]}'
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
        if args.date is None:
            args.date = time.strftime("%Y%m%d")
        query_table.add_row([args.start, args.end, args.date,
                             args.type, args.min_start_hour, args.max_start_hour, args.all])
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
        if self.chosen_ticket is None:
            return
        train_id = self.chosen_ticket["train_id"]
        for ticket in self.tickets:
            if ticket["train_id"] == train_id and ticket["has_ticket"] == 'Y':
                break
        else:
            print(f"The chosen train ID: {train_id} has been sold out!")
            self.chosen_ticket = None
            return
        self.chosen_ticket = ticket
        self.bot.print_ticket_info([self.chosen_ticket])
        print('The ticket shown above has been chosen successfully.')

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
    show_parser.add_argument('item', type=str, choices=['tickets', 'passengers', 'orders', 'chosen_ticket'])

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
        r = self.bot.qr_login()
        if r:
            print('Your related active passengers:')
            self.do_get_passengers("")

    clear_parser = cmd2.Cmd2ArgumentParser(description="Clear some list attributes.")
    clear_parser.add_argument("item", type=str, choices=['passengers', 'tickets', 'orders', 'chosen_ticket'])

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
        self.orders.clear()

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
        print('The ticket shown above has been chosen successfully.')

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
            print('The chosen passenger is not active!')
            return
        all_passenger_id = [order.get('id') for order in self.orders]
        if passenger_id in all_passenger_id:
            print('The chosen passenger is already in order list.')
            return
        added = {
            'id': passenger_id,
            "passenger": self.passengers[passenger_id - 1],
            "seat_type": args.seat_type,
            "ticket_type": str(args.ticket_type)
        }
        self.orders.append(added)
        self.bot.print_orders([added])
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
        print('The order shown above has been removed successfully.')

    def do_get_queue_count(self, args):
        """Query for the count of tickets left."""
        try:
            if self.chosen_ticket is None or not self.orders:
                print('Ticket and order information is not completed.')
                return
            submit_success, r = self.bot.submit_order_request(self.chosen_ticket)
            if submit_success:
                print('Submit Successfully!')
            if not submit_success:
                if r is not None:
                    print(r['messages'][0])
                    if "车票信息已过期" in r['messages'][0]:
                        print('Use \'update_tickets\' cmd and retry.')
                return
            status, r = self.bot.check_order_info(self.orders)
            if not status:
                if r is not None:
                    print(r['messages'][0])
                return
            seat_type = self.orders[0]['seat_type']
            status, r = self.bot.get_queue_count(seat_type)
            if not status:
                if r is not None:
                    print(r['messages'][0])
                return
            tickets_left = r['data']['ticket'].split(',')
            if len(tickets_left) == 2:
                print(f'查询成功,本次列车{self.bot.code2seat[seat_type]}余票 {tickets_left[0]} 张, 无座余票 {tickets_left[1]} 张')
            else:
                print(f'查询成功,本次列车{self.bot.code2seat[seat_type]}余票 {tickets_left[0]} 张')
        except Exception as e:
            print('Network Error, please try again!')
            print(e)

    def do_bye(self, args):
        """Say bye to the shell."""
        print('Thank you for using 12306 ticket bot shell.\nBye~')
        return True

    do_quit = do_bye


if __name__ == "__main__":
    sys.exit(TicketBotShell().cmdloop())
