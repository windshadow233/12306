import cmd2
from retry import retry
from prettytable import PrettyTable, ALL
import time


class TicketsCmd(object):

    def __init__(self):
        super(TicketsCmd, self).__init__()
        self.tickets = []
        self.selected_ticket = None
        self.last_queue_args = None

    search_parser = cmd2.Cmd2ArgumentParser(description='Search for tickets information')
    search_parser.add_argument('-s', '--start', type=str, required=True, help='Start Station')
    search_parser.add_argument('-e', '--end', type=str, required=True, help='Arrive Station')
    search_parser.add_argument('-d', '--date', type=str,
                               help='Date (format: %%Y%%m%%d, eg: 20210512, default: today)', default=None)
    search_parser.add_argument('-t', '--type', type=str.upper, help='Type of Train (The first letter of train number)',
                               choices=['G', 'D', 'K', 'T', 'Z'], default=None)
    search_parser.add_argument('-m', '--min_start_hour', type=int, choices=range(24), default=0,
                               help='The minimum start hour (0~23)')
    search_parser.add_argument('-M', '--max_start_hour', type=int, choices=range(1, 25), default=24,
                               help='The maximum start hour (1~24)')
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

    def print_query(self, args):
        query_table = PrettyTable(['出发站', '到达站', '日期', '类型', '最早发车时间', '最晚发车时间', '是否显示售罄'], hrules=ALL)
        query_table.add_row([args.start, args.end, args.date,
                             args.type or '--', args.min_start_hour, args.max_start_hour, args.all])
        print(query_table)

    def do_update_tickets(self, args):
        """Update tickets info by latest query"""
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
        print('Results of the above query has been updated successfully.')
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

    select_ticket_parser = cmd2.Cmd2ArgumentParser(description='Select a ticket to buy')
    select_ticket_parser.add_argument('id', type=int, help='Ticket ID in \'tickets\' list.')

    @retry(tries=10, delay=0.2)
    def select_ticket(self, ticket):
        submit_success, r = self.bot.submit_order_request(ticket)
        if submit_success:
            print('Submit ticket info successfully!')
        if not submit_success:
            if r is not None:
                print(r['messages'][0])
                if "车票信息已过期" in r['messages'][0]:
                    print('Use \'update_tickets\' cmd and retry.')
                    return 0
                elif r['messages'][0] == '当前时间不可以订票':
                    return -1
                else:
                    raise Exception
        self.bot.get_init_info()
        self.selected_ticket = ticket
        self.bot.print_ticket_info([ticket])
        self.__setattr__('need_queue', True)
        print('The ticket shown above has been selected successfully.')
        return 1

    @cmd2.with_argparser(select_ticket_parser)
    def do_select_ticket(self, args):
        if not self.bot.check_user()[0]:
            print('Please get login first.')
            return
        if not self.tickets:
            print('No tickets stored. Use \'search\' cmd to fetch.')
            return
        ticket_id = args.id
        if not 1 <= ticket_id <= len(self.tickets):
            print(f'Ticket ID out of range! Select \'{ticket_id}\', but the range is 1 ~ {len(self.tickets)}.')
            return
        has_ticket = self.tickets[ticket_id - 1].get('has_ticket') == 'Y'
        if not has_ticket:
            print('The ticket you select has been sold out!')
            return
        self.select_ticket(self.tickets[ticket_id - 1])
