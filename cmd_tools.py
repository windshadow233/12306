import cmd2
import sys
from ticket_bot import RailWayTicket


class TicketBotShell(cmd2.Cmd):
    intro = 'Welcome to the 12306 ticket bot shell. Type help or ? to list commands.\n' \
            'You need to ensure a stable network environment to use this shell.'
    prompt = '(12306)>'
    bot = RailWayTicket()
    tickets = []
    passengers = []

    search_parser = cmd2.Cmd2ArgumentParser(description='Search for tickets information')
    search_parser.add_argument('-s', '--start', type=str, help='Start Station')
    search_parser.add_argument('-e', '--end', type=str, help='Arrive Station')
    search_parser.add_argument('-d', '--date', type=str,
                               help='Date (format: %%Y%%m%%d, eg: 20210512, default: today)', default=None)
    search_parser.add_argument('-t', '--type', type=str.upper, help='Type of Train (The first letter of train number)',
                               choices=['G', 'D', 'K', 'T', 'Z'], default=None)
    search_parser.add_argument('-a', '--all', type=str.upper,
                               help='Whether to show tickets which have been sold out. (Default: N)',
                               choices=['Y', 'N'], default='N')

    @cmd2.with_argparser(search_parser)
    def do_search(self, args):
        if args.date is not None:
            args.date = f'{args.date[:4]}-{args.date[4: 6]}-{args.date[6:]}'
        self.tickets = self.bot.get_ticket_info(args.start, args.end, args.date, args.type, args.all == 'Y')
        print('The search results have been stored into \'tickets\' list')
        if self.tickets:
            self.bot.print_ticket_info(self.tickets)
        else:
            print('No tickets found, change the stations or date and try again.')

    show_parser = cmd2.Cmd2ArgumentParser(description='Show something')
    show_parser.add_argument('list', type=str, choices=['tickets', 'passengers'])

    @cmd2.with_argparser(show_parser)
    def do_show(self, args):
        if args.list == 'tickets':
            if not self.tickets:
                print('There is no tickets saved in cache. Use cmd \'search\' to fetch some.')
                return
            self.bot.print_ticket_info(self.tickets)
        else:
            self._show_passengers()

    login_parser = cmd2.Cmd2ArgumentParser(description='Get login')
    # login_parser.add_argument('-m', '--method', type=str,
    #                           help='Method to Login.\n'
    #                           'qr: to login with QR code\n'
    #                           'sms: to login with sms code(Usage count is limited in a day)',
    #                           choices=['qr', 'sms'], default='qr')
    # login_parser.add_argument('-u', '--user', type=str, help='User Name (Your Phone Number)')
    # login_parser.add_argument('-p', '--password', type=str, help='Your Password')
    # login_parser.add_argument('-c', '--cast_num', type=str, help='Last 4 digits of Your ID Card')

    @cmd2.with_argparser(login_parser)
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

    def _show_passengers(self):
        """Show your related passengers if you're login."""
        if not self.bot.check_login():
            print('Please login first.')
            return
        if self.passengers:
            print("Read passengers' data from cache.\n(Use cmd 'clear' first if you want to reload them)")
        else:
            self.passengers = self.bot.get_passengers()
        self.bot.print_passengers(self.passengers)

    clear_parser = cmd2.Cmd2ArgumentParser(description="Clear some list attributes.")
    clear_parser.add_argument("list", type=str, choices=['passengers', 'tickets'])

    @cmd2.with_argparser(clear_parser)
    def do_clear(self, args):
        self.__getattribute__(args.list).clear()

    def do_logout(self, args):
        """Get logout."""
        self.bot.logout()
        self.passengers.clear()

    def do_is_login(self, args):
        """Check whether you're login or not."""
        print(self.bot.check_login())

    def do_bye(self, args):
        """Say bye to the shell."""
        print('Thank you for using 12306 ticket bot shell.\nBye~')
        return True

    do_quit = do_bye


if __name__ == "__main__":
    sys.exit(TicketBotShell().cmdloop())
