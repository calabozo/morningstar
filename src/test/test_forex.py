import pytest
from datetime import datetime as dt

from pyfunds import Forex, ValueInfo


def test_wrong_pair():
    with pytest.raises(Exception) as fx_exception:
        fx = Forex(fx_base="PESETA", fx_trade="EUR")
    assert "Invalid FX pair" in str(fx_exception.value)


def test_get_token():
    fx = Forex(fx_base="EUR", fx_trade="USD")
    token = fx._get_token(2020, 11)
    assert len(token) == 32


def test_get_month():
    year = 2020
    month = 12
    fx = Forex(fx_base="EUR", fx_trade="USD")
    token = fx._get_token(year, month)
    df_data = fx._get_month(year, month, token)
    assert df_data.shape[0] > 5000
    assert df_data.shape[1] == 5
    assert df_data.index.month.unique()[0] == month


def test_forex():
    start_date = dt(2020, 10, 1)
    end_date = dt(2020, 12, 31)
    fx = Forex(fx_base="EUR", fx_trade="USD", start_date=start_date, end_date=end_date)
    assert fx.fx_inverted == False
    df_values = fx.get_forex()
    assert df_values.shape[0] > 5000
    assert df_values.shape[1] == 5
    assert all(df_values.index.month.unique().sort_values() == [10,11,12])

    fx_inv = Forex(fx_base="USD", fx_trade="EUR", start_date=start_date, end_date=end_date)
    assert fx_inv.fx_inverted == True
    df_values_inv = fx_inv.get_forex()
    assert 1.0 == pytest.approx( (df_values_inv["open"] * df_values["open"]).unique(), 0.01)

    df_weekly_return, _ = fx_inv.calc_roi_var(num_days=7)
    mean_values = df_weekly_return.mean(skipna=True).dropna()
    assert df_weekly_return.shape[0] > 5000
    assert df_weekly_return.shape[1] == 5
    assert all(mean_values.between(0.5, 1.5))


def test_forex_2019():
    start_date = dt(2019, 10, 1)
    end_date = dt(2020, 12, 31)
    fx = Forex(fx_base="EUR", fx_trade="USD", start_date=start_date, end_date=end_date)
    assert fx.fx_inverted == False
    df_values = fx.get_forex()
    assert df_values.shape[0] > 5000
    assert df_values.shape[1] == 5
    assert all(df_values.index.month.unique().sort_values() == [1,2,3,4,5,6,7,8,9,10,11,12])
    assert all(df_values.index.year.unique().sort_values() == [2019,2020])