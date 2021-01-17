import pytest
import pyfunds.simulation as simulation
from pyfunds import ValueInfo
import pandas as pd
import numpy as np

def test_build_orders():
    orders = simulation.Orders()
    orders.add_buy_order("2020-01-01")
    orders.add_sell_order("2020-01-02")
    orders.add_buy_order("2020-01-05")

    with pytest.raises(simulation.WrongOrderDateException) as order_exception:
        orders.add_sell_order("2020-01-05")
    assert "ERROR: Last order date" in str(order_exception.value)
    orders.add_sell_order("2020-01-06")

    assert orders.orders.shape == (4, 2)


def test_simulation():
    orders = simulation.Orders()
    orders.add_buy_order("2020-01-02")
    orders.add_sell_order("2020-01-04")
    orders.add_buy_order("2020-01-06")
    orders.add_sell_order("2020-01-10")

    df_fake = pd.DataFrame({'date': pd.date_range(start='2020-01-01', end='2020-01-11', freq='D'), 'myval': np.NaN})
    df_fake = df_fake.set_index("date")
    df_fake.loc[df_fake.index == "2020-01-01", "myval"] = 10
    df_fake.loc[df_fake.index == "2020-01-03", "myval"] = 12
    df_fake.loc[df_fake.index == "2020-01-05", "myval"] = 15

    df_fake.loc[df_fake.index == "2020-01-07", "myval"] = 16
    df_fake.loc[df_fake.index == "2020-01-09", "myval"] = 16
    df_fake.loc[df_fake.index == "2020-01-11", "myval"] = 17
    df_fake = df_fake.dropna()
    values = ValueInfo(df_fake)

    sim = simulation.Simulation(values, col="myval")
    roi = sim.calc_for_orders(orders)
    assert pytest.approx(roi, 1e-2) == 15/12 * 17/16
