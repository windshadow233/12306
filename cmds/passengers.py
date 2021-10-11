import cmd2


class PassengersCmd(object):
    def __init__(self):
        self.passengers = []
        self.passenger_strs = []
        self.passenger_old_strs = []

    get_passenger_parser = cmd2.Cmd2ArgumentParser(description='Get your related passengers')
    get_passenger_parser.add_argument('-a', '--all', action='store_true',
                                      help='If set, show all non-active passengers.')

    @cmd2.with_argparser(get_passenger_parser)
    def do_get_passengers(self, args):
        if not self.bot.check_user()[0]:
            print('Please get login first.')
            return
        else:
            self.passengers = self.bot.get_passengers(args.all)
        self.bot.print_passengers(self.passengers)
        print('The passenger results have been stored into \'passengers\' list.')
