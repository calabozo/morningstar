import pytest
from datetime import datetime as dt

from pyfunds import MorningStar
from utils import calc_annual_return, calc_roi


def test_get_ticket():
    m = MorningStar()
    ticket = m.get_ticket(ISIN="IE00B4K9F548")
    assert ticket['SecId'] == 'F00000O3W4'
    assert ticket['Name'] == 'iShares Europe Index (IE) Instl Acc EUR'
    assert ticket['PriceCurrency'] == 'EUR'
    assert ticket['LegalName'] == 'iShares Europe Index Fund (IE) Institutional Acc EUR'
    assert ticket['StarRatingM255'] >= 0
    assert ticket['QuantitativeRating'] >= 0


def test_get_historical_data_from_ticket():
    m = MorningStar()
    ticket = {'SecId': 'F00000O3W4', 'PriceCurrency': 'EUR'}
    start_date = dt(2019, 1, 1)
    end_date = dt(2019, 1, 31)
    df_values = m.get_historical_data_from_ticket(ticket, start_date, end_date)
    assert df_values.shape == (31, 2)
    assert all(df_values.columns == ['date', 'value'])
    assert df_values.value.mean() == 4.11


def test_get_historical_data_from_ISIN():
    m = MorningStar()
    isin = "IE00B4K9F548"
    start_date = dt(2019, 1, 1)
    df_values = m.get_historical_data_from_ISIN(ISIN=isin, start_date=start_date)
    assert df_values.shape[0] > 700
    assert df_values.shape[1] == 1
    assert df_values.columns[0] == isin
    assert df_values.index.name == 'date'

    df_values_dollar = m.get_historical_data_from_ISIN(ISIN=isin, start_date=start_date, currency='USD')
    assert df_values.shape == df_values_dollar.shape  # Possible blinker if it is executed exactly between to days
    assert df_values.columns[0] == isin
    assert df_values.index.name == 'date'
    ratio_eur_dollar_2019 = (df_values.loc[df_values.index <= '2019-12-31', isin] / df_values_dollar.loc[
        df_values.index <= '2019-12-31', isin]).mean()
    assert pytest.approx(ratio_eur_dollar_2019, 0.01) == 1.17


def test_get_historical_data_ISIN_list():
    m = MorningStar()
    isins = ["IE00B4K9F548", "LU0389812933", "LU0996180864"]
    start_date = dt(2019, 1, 1)

    df_values = m.get_historical_data_ISIN_list(ISINs=isins, start_date=start_date, currency='EUR')
    df_values = df_values[df_values.index <= '2019-12-31']
    assert df_values.shape == (365, len(isins))
    assert all(df_values.columns == isins)
    assert df_values.index.name == 'date'
    assert pytest.approx(df_values[isins[0]].mean(), 0.01) == 15.944
    assert pytest.approx(df_values[isins[1]].mean(), 0.01) == 3.5381
    assert pytest.approx(df_values[isins[2]].mean(), 0.01) == 12.159

    df_weekly_return = calc_roi(df_values, num_days=7)
    mean_values = df_weekly_return.mean(skipna=True)
    assert df_weekly_return.shape[0] <= 365 - 6
    assert df_weekly_return.shape[1] == len(isins)
    assert all(mean_values.between(0.5 , 1.5))

