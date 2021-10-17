import cmd2


class PassengersCmd(object):
    def __init__(self):
        self.passengers = []

    def get_passengers(self, args):
        if not self.bot.check_user()[0]:
            print('Please get login first.')
            return
        else:
            self.passengers = self.bot.get_passengers(args.all)
        self.bot.print_passengers(self.passengers)
        print('The passenger results have been stored into \'passengers\' list.')

    def show_passengers(self, args):
        if not self.passengers:
            print('No passengers saved in cache! Use \'passenger get\' cmd to fetch.')
            return
        self.bot.print_passengers(self.passengers)

    def clear_passengers(self, args):
        self.passengers.clear()
        print('Passengers cleared.')

    passenger_parser = cmd2.Cmd2ArgumentParser(description='Passenger Commands')
    passenger_sub_parser = passenger_parser.add_subparsers()
    get_passenger_parser = passenger_sub_parser.add_parser(name='get', help='Get your related passengers')
    get_passenger_parser.add_argument('-a', '--all', action='store_true',
                                      help='If set, show all non-active passengers')
    show_passenger_parser = passenger_sub_parser.add_parser(name='show', help='Show saved passengers')
    clear_passenger_parser = passenger_sub_parser.add_parser(name='clear', help='Clear saved passengers')

    get_passenger_parser.set_defaults(func=get_passengers)
    show_passenger_parser.set_defaults(func=show_passengers)
    clear_passenger_parser.set_defaults(func=clear_passengers)

    @cmd2.with_argparser(passenger_parser)
    def do_passenger(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('ticket')
