import pytest
from datetime import datetime as dt

from pyfunds import MorningStar, ValueInfo
from pyfunds.morningstar import get_ticket, get_historical_data_from_ticket, get_key_stats_from_ticket
import numpy as np

def test_get_ticket():
    ticket = get_ticket(ISIN="IE00B4K9F548")
    assert ticket['SecId'] == 'F00000O3W4'
    assert ticket['Name'] == 'iShares Europe Index (IE) Instl Acc EUR'
    assert ticket['PriceCurrency'] == 'EUR'
    assert ticket['LegalName'] == 'iShares Europe Index Fund (IE) Institutional Acc EUR'
    assert ticket['StarRatingM255'] >= 0
    assert ticket['QuantitativeRating'] >= 0

def test_key_stats_from_ticket():
    ticket = get_key_stats_from_ticket(SecId="F00000O3W4")
    assert ticket['Charge'] == 0.29
    assert ticket['ISIN'] == 'IE00B4K9F548'


def test_get_historical_data_from_ticket():
    ticket = {'SecId': 'F00000O3W4', 'PriceCurrency': 'EUR'}
    start_date = dt(2019, 1, 1)
    end_date = dt(2019, 1, 31)
    df_values = get_historical_data_from_ticket(ticket, start_date, end_date)
    assert df_values.shape == (31, 2)
    assert all(df_values.columns == ['date', 'value'])
    assert pytest.approx(df_values.value.mean(),0.01) == 104.11


def test_get_historical_data_from_ISIN():
    m = MorningStar(ISINs=None)
    isin = "IE00B4K9F548"
    start_date = dt(2019, 1, 1)
    df_values = m._get_historical_data_from_ISIN(ISIN=isin, start_date=start_date)
    assert df_values.shape[0] > 700
    assert df_values.shape[1] == 1
    assert df_values.columns[0] == isin
    assert df_values.index.name == 'date'

    df_values_dollar = m._get_historical_data_from_ISIN(ISIN=isin, start_date=start_date, currency='USD')
    assert df_values.shape == df_values_dollar.shape  # Possible blinker if it is executed exactly between to days
    assert df_values.columns[0] == isin
    assert df_values.index.name == 'date'
    ratio_eur_dollar_2019 = ((df_values.loc[df_values.index <= '2019-12-31', isin] - 100)/
                             (df_values_dollar.loc[df_values_dollar.index <= '2019-12-31', isin] - 100)).mean()
    assert pytest.approx(ratio_eur_dollar_2019, 0.01) == 1.17


def test_get_historical_data_ISIN_list():
    isins = ["IE00B4K9F548", "LU0389812933", "LU0996180864"]
    num_days_roi = 7
    start_date = dt(2019, 1, 1)
    m = MorningStar(ISINs=isins, start_date=start_date, currency='EUR')

    df_values = m.df_values
    df_values = df_values[df_values.index <= '2019-12-31']
    assert df_values.shape == (365, len(isins))
    assert all(df_values.columns == isins)
    assert df_values.index.name == 'date'
    assert pytest.approx(df_values[isins[0]].mean(), 0.01) == 115.944
    assert pytest.approx(df_values[isins[1]].mean(), 0.01) == 103.5381
    assert pytest.approx(df_values[isins[2]].mean(), 0.01) == 112.159

    assert m.tickets['IE00B4K9F548']['Charge'] > 0
    assert m.tickets['LU0389812933']['Charge'] > 0

    assert all(np.array(m.get_annual_charges()) > 0)

    df_weekly_return, _ = m.calc_roi_var(num_days=num_days_roi)
    df_weekly_return_no_charge, _ = m.calc_roi_var(num_days=num_days_roi, annual_charges_percentage=[0, 0, 0])

    mean_values = df_weekly_return.mean(skipna=True)
    assert df_weekly_return.shape[0] == (m.df_values.shape[0]-num_days_roi+1)
    assert df_weekly_return.shape[1] == len(isins)
    assert all(mean_values.between(0.5 , 1.5))
    assert (df_weekly_return_no_charge.dropna().values >= df_weekly_return.dropna().values).all()

