from datetime import timedelta, date
from pyfunds.simulation import OrderType
import pyfunds.simulation as simulation


def daterange(from_date, to_date):
    for n in range(int((to_date - from_date).days)):
        yield from_date + timedelta(n)

class MainRobot:

    orders = None

    def __init__(self):
        pass

    def train(self, value_info):
        pass

    def calc_buy_order(self, values):
        pass

    def calc_sell_order(self, values):
        pass

    def test(self, value_info, from_date, to_date):
        orders = simulation.Orders()
        next_order = OrderType.BUY
        for mydate in daterange(from_date, to_date):
            values = value_info.get_data(max_date=mydate)
            if next_order == OrderType.BUY:
                if self.calc_buy_order(values):
                    orders.add_buy_order(mydate)
                    next_order = OrderType.SELL
            elif next_order == OrderType.SELL:
                if self.calc_sell_order(mydate):                    
                    orders.add_sell_order(mydate) 
                    next_order = OrderType.BUY
        return orders
               



