import pandas as pd
from .valueinfo import ValueInfo

from enum import Enum


class WrongOrderDateException(Exception):
    pass


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    CONDITIONAL_SELL = "CONDITIONAL_SELL"
    CONDITIONAL_BUY = "CONDITIONAL_BUY"


class Orders:

    def __init__(self, buy_fee=0, sell_fee=0):
        self.orders = pd.DataFrame(columns=["date", "type"])
        self.buy_fee = 0
        self.sell_fee = 0

    def add_order(self, date: pd.Timestamp, order_type: OrderType):
        if self.orders.shape[0] > 0:
            last_order = self.orders.iloc[-1]
            if last_order.type == order_type:
                print(f"Warning: Last order date:{last_order.date} was of type {last_order.type}")
            if last_order.date >= date:
                raise WrongOrderDateException(f"ERROR: Last order date:{last_order.date}")
        self.orders = self.orders.append({"date": date, "type": order_type}, ignore_index=True)

    def add_buy_order(self, date):
        self.add_order(pd.to_datetime(date), OrderType.BUY)

    def add_sell_order(self, date):
        self.add_order(pd.to_datetime(date), OrderType.SELL)

    def get_num_orders(self):
        return self.orders.shape[0]

    def __iter__(self):
        return OrdersIterator(self)


class OrdersIterator:

    def __init__(self, orders):
        # Team object reference
        self._orders = orders
        # member variable to keep track of current index
        self._index = 0

    def __next__(self):
        ''''Returns the next value from team object's lists '''
        if self._index < self._orders.get_num_orders():
            result = self._orders.orders.iloc[self._index]
            self._index += 1
            return result
        # End of Iteration
        raise StopIteration


class Simulation:

    def __init__(self, valueinfo: ValueInfo, col):
        self.valueinfo = valueinfo
        self.valueinfo._sort()
        self.column = col

    def calc_for_orders(self, orders: OrderType):
        total_inc = 1
        buy_value = None

        for order in orders:
            diff_days = (self.valueinfo.df_values.index - order["date"]).total_seconds()
            value = self.valueinfo.df_values[diff_days >= 0].iloc[0][self.column]
            if order.type == OrderType.BUY:
                buy_value = value
            elif order.type == OrderType.SELL:
                total_inc = total_inc * value/buy_value
        return total_inc
