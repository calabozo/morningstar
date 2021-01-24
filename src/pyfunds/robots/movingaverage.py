import random
import pyfunds.simulation as simulation
from pyfunds.robots import MainRobot


class MovingAverage(MainRobot):

    def __init__(self, short_period=5, long_period=60):
        if short_period>=long_period:
            raise Exception(f"Error: short_period={short_period} must be lower than long_period={long_period}"
        self.short_period=short_period
        self.long_period=long_period

    def _calc_buy_sell(self, df_values):
        mn_short_now= df_values.iloc[-short_period:-1,0].mean()
        mn_long_now = df_values.iloc[-long_period:-1,0].mean()
        if mn_long_now<mn_short:
            return True
        else:
            return False


    def calc_buy_order(self, df_values):
        return self._calc_buy_sell(df_falues)

    def calc_sell_order(self, df_values):
        return !self._calc_buy_sell(df_falues)


