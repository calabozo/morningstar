import pytest
from datetime import datetime as dt

from pyfunds import Forex, ValueInfo


def test_get_token():
    fx = Forex(fxpair="eurusd")
    token = fx._get_token(2020, 11)
    assert len(token) == 32


def test_get_month():
    year = 2020
    month = 12
    fx = Forex(fxpair="eurusd")
    token = fx._get_token(year, month)
    df_data = fx._get_month(year, month, token)
    assert df_data.shape[0] > 5000
    assert df_data.shape[1] == 5
