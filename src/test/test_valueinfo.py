import pytest
import pandas as pd
import numpy as np
from pyfunds import ValueInfo


@pytest.fixture
def foo_info():
    df_fake = pd.DataFrame({'date': pd.date_range(start='2010-01-07', end='2020-12-31', freq='D'),
                            'fund1': 1.0001, 'fund2': 30})
    df_fake['fund3'] = np.random.normal(loc=15, scale=1, size=df_fake.shape[0])
    df_fake['fund4'] = df_fake["fund1"].cumprod()
    df_fake = df_fake.set_index('date')

    return ValueInfo(df_fake)


def test_roi(foo_info):
    df_roi, _ = foo_info.calc_roi_var()
    assert foo_info.df_values.shape == (4012, 4)
    assert df_roi.shape == (4012 - 364, 4)
    assert all(df_roi['fund1'] == 1)
    assert all(df_roi['fund2'] == 1)
    assert df_roi['fund3'].mean() < 1.01
    assert df_roi['fund3'].var() > 0
    assert pytest.approx(df_roi['fund4'].var(), 1e-10) == 0
    assert pytest.approx(df_roi.loc['2015-01-31', 'fund4'], 0.01) == 1.037


def test_var(foo_info):
    _, df_var = foo_info.calc_roi_var()
    assert foo_info.df_values.shape == (4012, 4)
    assert df_var.shape == (4012 - 364 - 364, 4)
    assert all(df_var['fund1'] == 0)
    assert all(df_var['fund2'] == 0)
    assert df_var['fund3'].mean() < 1.2
    assert pytest.approx(df_var.loc['2015-01-31', 'fund4'], 1e-10) == 0


def test_annual_return(foo_info):
    df_return = foo_info.calc_annual_return()
    assert all(df_return['fund1'] == 1)
    assert all(df_return['fund2'] == 1)
    assert df_return['fund3'].mean() > 0.7
    assert df_return['fund3'].var() > 0
    assert 0 == pytest.approx(df_return['fund4'].var(), 1e-10)
    assert 1.037 == pytest.approx(df_return.loc[2015, 'fund4'], 0.01)


def test_annual_var(foo_info):
    df_var = foo_info.calc_annual_var()
    assert all(df_var['fund1'] == 0)
    assert all(df_var['fund2'] == 0)
    assert df_var['fund3'].mean() > 0
    assert df_var['fund3'].var() > 0
    assert pytest.approx(df_var.loc[2015, 'fund4'], 0.01) == 0
    assert all(df_var['fund4'] == 0)