import cmd2
from ticket_bot import RailWayTicket


class TicketBotShell(cmd2.Cmd):
    intro = 'Welcome to the 12306 ticket bot shell. Type help or ? to list commands.\n'
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
                               choices=['G', 'D', 'K', 'T', 'Z', None], default=None)

    @cmd2.with_argparser(search_parser)
    def do_search(self, args):
        if args.date is not None:
            args.date = f'{args.date[:4]}-{args.date[4: 6]}-{args.date[6:]}'
        self.tickets = self.bot.get_ticket_info(args.start, args.end, args.date, args.type)
        if self.tickets:
            self.bot.print_ticket_info(self.tickets)
        else:
            print('未找到票源,请更改日期或站名~')

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

    def do_show_passengers(self, args):
        if not self.bot.check_login():
            print('Please login first.')
            return
        self.passengers = self.bot.get_passengers()
        self.bot.print_passengers(self.passengers)

    def do_logout(self, args):
        """Get logout."""
        self.bot.logout()

    def do_is_login(self, args):
        """Check whether you're login or not."""
        print(self.bot.check_login())

    def do_quit(self, args):
        """Quit the shell."""
        print('Thank you for using 12306 ticket bot shell.\nBye~')
        return True

    def do_bye(self, args):
        return self.do_quit(args)


if __name__ == "__main__":
    TicketBotShell().cmdloop()
