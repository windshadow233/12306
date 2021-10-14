import cmd2
from retry import retry


class OrderCmd(object):

    def __init__(self):
        self.orders = []

    add_order_parser = cmd2.Cmd2ArgumentParser(description="Add a piece of order")
    add_order_parser.add_argument('id', type=int,
                                  help='Passenger ID in \'passengers\' list.')

    @cmd2.with_argparser(add_order_parser)
    def do_add_order(self, args):
        passengers = self.__getattribute__('passengers')
        if not passengers:
            print('No passengers stored. Use \'get_passengers\' cmd to fetch.')
            return
        passenger_id = args.id
        if not 1 <= passenger_id <= len(passengers):
            print(f'Passenger ID out of range! Choose {passenger_id}, but the range is 1 ~ {len(passengers)}.')
            return
        is_active = passengers[passenger_id - 1]['if_receive']
        if is_active != 'Y':
            print('The chosen passenger is not active!')
            return
        for order in self.orders:
            if passenger_id == order.get('id'):
                print('The chosen passenger is already in order list.')
                return
        passenger = passengers[passenger_id - 1]
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
            "passenger": passenger,
            "seat_type": seat_type,
            "ticket_type": ticket_type,
            "choose_seat": choose_seat
        }
        self.orders.append(added)
        self.__getattribute__('passenger_strs').append(
            self.bot.generate_passenger_ticket_str(passenger, seat_type, ticket_type))
        self.__getattribute__('passenger_old_strs').append(self.bot.generate_old_passenger_str(passenger))
        self.bot.print_orders([added])
        self.__setattr__('need_queue', True)
        print('Order info shown above has been added Successfully.')

    rm_order_parser = cmd2.Cmd2ArgumentParser(description='Remove a piece of order')
    rm_order_parser.add_argument('id', type=int, help='Order ID in \'order\' list.')

    @cmd2.with_argparser(rm_order_parser)
    def do_rm_order(self, args):
        if not self.orders:
            print('No order stored. Use \'add_order\' cmd to add.')
            return
        order_id = args.id
        if not 1 <= order_id <= len(self.orders):
            print(f'Order ID out of range! Choose {order_id}, but the range is 1 ~ {len(self.orders)}.')
            return
        self.bot.print_orders([self.orders.pop(order_id - 1)])
        self.__getattribute__('passenger_strs').pop(order_id - 1)
        self.__getattribute__('passenger_old_strs').pop(order_id - 1)
        self.__setattr__('need_queue', True)
        print('The order shown above has been removed successfully.')

    @retry(tries=10, delay=0.5)
    def do_queue_count(self, args):
        """Query for the count of tickets left"""
        if not self.bot.check_user()[0]:
            print('Please get login first.')
            return
        if self.__getattribute__('selected_ticket') is None or not self.orders:
            print('Ticket or order information is not completed.')
            return
        status, r = self.bot.check_order_info(self.__getattribute__('passenger_strs'),
                                              self.__getattribute__('passenger_old_strs'))
        if not status:
            print(r['messages'][0])
            return
        seat_type = self.orders[0]['seat_type']
        status, r = self.bot.get_queue_count(seat_type)
        if not status:
            print(r['messages'][0])
            print('可能原因是您选择的席位余票不足或车票信息过期，建议更换席位或更新车票信息并再次尝试')
            return
        tickets_left = r['data']['ticket'].split(',')
        if len(tickets_left) == 2:
            print(f'查询成功,本次列车{self.bot.seat_type_dict[seat_type]}余票 {tickets_left[0]} 张, 无座余票 {tickets_left[1]} 张')
        else:
            print(f'查询成功,本次列车{self.bot.seat_type_dict[seat_type]}余票 {tickets_left[0]} 张')
        self.__setattr__('need_queue', False)

    @retry(tries=20)
    def do_confirm(self, args):
        """Confirm your orders"""
        selected_ticket = self.__getattribute__('selected_ticket')
        if selected_ticket is None or not self.orders:
            print('Ticket or order information is not completed.')
            return
        if self.__getattribute__('need_queue'):
            print('Please queue for count first!')
            return
        seats = ''
        for i, order in enumerate(self.orders, 1):
            seat = order['choose_seat']
            if seat:
                seats += f'{i}{seat}'
        success, r = self.bot.confirm_single_for_queue(self.__getattribute__('passenger_strs'),
                                                       self.__getattribute__('passenger_old_strs'), seats)
        if success:
            print('Congratulations!!!Please go to 12306 APP and pay for your tickets!')
            self.bot.print_ticket_info([selected_ticket])
            self.bot.print_orders(self.orders)
        else:
            raise Exception
