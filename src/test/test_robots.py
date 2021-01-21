import pytest
from pyfunds.robots import CrazyMonkey
from pyfunds import ValueInfo
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

    crazy_monkey = CrazyMonkey(0)
    assert crazy_monkey.calc_buy_order(values)==True
    assert crazy_monkey.calc_sell_order(values)==True
    orders = crazy_monkey.test(values, from_date=dt(2020,1,1), to_date=dt(2020,1,11))
    assert orders.get_num_orders() == 10
    print(orders)

    sim = simulation.Simulation(values, col="myval")
    roi = sim.calc_for_orders(orders)
    print(sim)
    assert roi > 1.0

