import pytest
from pyfunds.robots import CrazyMonkey, MovingAverage
from pyfunds import ValueInfo, MorningStar
import pandas as pd
import numpy as np
from datetime import datetime as dt
import pyfunds.simulation as simulation


def test_crazy_monkey():
    df_fake = pd.DataFrame({'date': pd.date_range(start='2020-01-01', end='2020-01-11', freq='D'), 'myval': 7})
    df_fake = df_fake.set_index("date")
    df_fake.loc[df_fake.index == "2020-01-01", "myval"] = 10
    df_fake.loc[df_fake.index == "2020-01-02", "myval"] = 15
    df_fake.loc[df_fake.index == "2020-01-03", "myval"] = 12
    df_fake.loc[df_fake.index == "2020-01-04", "myval"] = 16
    df_fake.loc[df_fake.index == "2020-01-05", "myval"] = 18

    df_fake.loc[df_fake.index == "2020-01-08", "myval"] = 16
    df_fake.loc[df_fake.index == "2020-01-09", "myval"] = 16
    df_fake.loc[df_fake.index == "2020-01-10", "myval"] = 20
    df_fake.loc[df_fake.index == "2020-01-11", "myval"] = 17
    df_fake = df_fake.dropna()
    values = ValueInfo(df_fake)

    crazy_monkey = CrazyMonkey(values, column_value="myval", p_rate=0)
    assert crazy_monkey.calc_buy_order(None) == True
    assert crazy_monkey.calc_sell_order(None) == True
    orders = crazy_monkey.test(from_date=dt(2020, 1, 1), to_date=dt(2020, 1, 11))
    assert orders.get_num_orders() == 10
    print(orders)

    sim = simulation.Simulation(values, col="myval")
    roi = sim.calc_for_orders(orders)
    print(sim)
    assert roi > 1.0


def test_moving_average():
    isins = ["IE00B4K9F548"]
    m = MorningStar(ISINs=isins)
    ma = MovingAverage(value_info=m, column_value=isins[0], short_period=5, long_period=100)
    orders = ma.test( from_date=dt(2020, 1, 1), to_date=dt(2020, 12, 31))
    assert orders.get_num_orders() > 0

    sim = simulation.Simulation(m, col=isins[0])
    roi = sim.calc_for_orders(orders)
    assert roi > 0
    print(sim)
