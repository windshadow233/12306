import cmd2


class LoginCmd(object):

    login_parser = cmd2.Cmd2ArgumentParser(description='Get login')
    login_parser.add_argument('-m', '--method', type=str,
                              help='Method to Login.\n'
                              'qr: to login with QR code\n'
                              'sms: to login with sms code (Usage count is limited in a day)',
                              choices=['qr', 'sms'], default='qr')
    login_parser.add_argument('-u', '--user', type=str, help='User Name (Your Phone Number)')

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
            self.__setattr__("passengers", self.bot.get_passengers())
            self.bot.print_passengers(self.__getattribute__('passengers'))
            print('The passenger results have been stored into \'passengers\' list.')

    def do_check_user(self, args):
        """Check whether you're login or not."""
        status, username = self.bot.check_user()
        if status:
            print(f'You\'re login. Current user: {username}')
        else:
            print(f'You\'re not login.')

