import random
import pyfunds.simulation as simulation
from pyfunds.robots import MainRobot


class CrazyMonkey(MainRobot):

    def __init__(self, p_rate=0.1):
        self.p_rate=p_rate

    def calc_buy_order(self, df_values):
        p = random.random()
        if p>=self.p_rate:
            return True
        else:
            return False

    def calc_sell_order(self, df_values):
        p = random.random()
        if p>=self.p_rate:
            return True
        else:
            return False


