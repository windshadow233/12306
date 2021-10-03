import argparse
from ticket_bot import RailWayTicket

parser = argparse.ArgumentParser(description='Search for tickets information')
parser.add_argument('-s', '--start', type=str, help='Start Station')
parser.add_argument('-e', '--end', type=str, help='Arrive Station')
parser.add_argument('-d', '--date', type=str, help='Date (format: %Y%m%d, eg: 20210512)', default=None)
parser.add_argument('-t', '--type', type=str.upper, help='Type of Train',
                    choices=['G', 'D', 'K', 'T', 'Z', None], default=None)
parser.add_argument('-l', '--login', type=str.upper, help='Whether to Login', choices=['Y', 'N'], default='N')
parser.add_argument('-m', '--login_method', type=str, help='Method for Login', choices=['qr', 'sms'], default='qr')
parser.add_argument('-u', '--user', type=str, help='User Name (Your Phone Number)')
parser.add_argument('-p', '--password', type=str, help='Your Password')
parser.add_argument('-c', '--cast_num', type=str, help='Last 4 digits of Your ID Card')

args = parser.parse_args()

bot = RailWayTicket()

if args.login == 'Y':
    if args.login_method == 'sms':
        if not args.user:
            print('未提供手机号!(-u)')
            exit(-1)
        if not args.password:
            print('未提供密码!(-p)')
            exit(-1)
        if not args.cast_num:
            print('未提供身份证后四位!(-c)')
            exit(-1)
        bot.sms_login(args.user, args.password, args.cast_num)
    else:
        bot.qr_login()
if args.date is not None:
    date = f'{args.date[:4]}-{args.date[4: 6]}-{args.date[6:]}'
tickets = bot.get_ticket_info(from_=args.start, to_=args.end, date=date, train_type=args.type)
if tickets:
    bot.print_ticket_info(tickets)
else:
    print('未找到票源,请更改日期或站名~')

