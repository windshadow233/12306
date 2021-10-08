import requests
from bot.login import Login
from bot.passengers import Passengers
from bot.tickets import Tickets
from bot.order import Order


class RailWayTicketBot(Login, Passengers, Tickets, Order):

    submit_token = ""
    ticketInfoForPassengerForm = None

    def __init__(self):
        self.sess = requests.session()
        self.sess.get('https://kyfw.12306.cn')
        Login.__init__(self)
        Passengers.__init__(self)
        Tickets.__init__(self)
        Order.__init__(self)

        self.sess.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn',
            'Origin': 'https://kyfw.12306.cn'
        }


if __name__ == "__main__":
    bot = RailWayTicketBot()
    bot.qr_login()
