import cmd2


class LoginCmd(object):

    def qr_login(self, args):
        r = self.bot.qr_login()
        return r

    def sms_login(self, args):
        if not args.user:
            print('未提供手机号!(-u)')
            return
        r = self.bot.sms_login(args.user)
        return r

    def check_user(self, args):
        status, username = self.bot.check_user()
        if status:
            print(f'You\'re login. Current user: {username}')
        else:
            print(f'You\'re not login.')

    login_parser = cmd2.Cmd2ArgumentParser(description='Login Commands')
    login_sub_parsers = login_parser.add_subparsers()
    qr_login_parser = login_sub_parsers.add_parser(name='qr', help='Login with QR code')
    sms_login_parser = login_sub_parsers.add_parser(name='sms', help='Login with sms message')
    sms_login_parser.add_argument('-u', '--user', type=str, help='User Name (Your Phone Number)')
    login_check_parser = login_sub_parsers.add_parser(name='check', help='Check login status')

    qr_login_parser.set_defaults(func=qr_login)
    sms_login_parser.set_defaults(func=sms_login)
    login_check_parser.set_defaults(func=check_user)

    @cmd2.with_argparser(login_parser)
    def do_login(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            r = func(self, args)
        else:
            r = self.qr_login(args)
        if r:
            print('Your related active passengers:')
            self.__setattr__("passengers", self.bot.get_passengers())
            self.bot.print_passengers(self.__getattribute__('passengers'))
            print('The passenger results have been stored into \'passengers\' list.')
