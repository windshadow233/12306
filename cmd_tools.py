import cmd2
import sys
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
    sys.exit(TicketBotShell().cmdloop())
