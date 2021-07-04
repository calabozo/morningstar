#!/usr/bin/python3
import time
from collections import ChainMap
from typing import Tuple

import requests
import json
import datetime
from datetime import datetime as dt
import pandas as pd
from .valueinfo import ValueInfo, _roi
import bs4 as bs
import numpy as np


def get_ticket(ISIN: str, errors='ignore') -> dict:
    url = f"https://lt.morningstar.com/api/rest.svc/klr5zyak8x/security/screener?page=1&pageSize=10&sortOrder=LegalName%20asc&outputType=json&version=1&languageId=es-ES&currencyId=EUR&universeIds=FOESP%24%24ALL&securityDataPoints=SecId%7CName%7CPriceCurrency%7CTenforeId%7CLegalName%7CClosePrice%7CYield_M12%7CCategoryName%7CAnalystRatingScale%7CStarRatingM255%7CQuantitativeRating%7CSustainabilityRank%7CReturnD1%7CReturnW1%7CReturnM1%7CReturnM3%7CReturnM6%7CReturnM0%7CReturnM12%7CReturnM36%7CReturnM60%7CReturnM120%7CFeeLevel%7CManagerTenure%7CMaxDeferredLoad%7CInitialPurchase%7CFundTNAV%7CEquityStyleBox%7CBondStyleBox%7CAverageMarketCapital%7CAverageCreditQualityCode%7CEffectiveDuration%7CMorningstarRiskM255%7CAlphaM36%7CBetaM36%7CR2M36%7CStandardDeviationM36%7CSharpeM36%7CTrackRecordExtension&filters=&term={ISIN}"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Error, unexpected HTTP response code: {r.status_code}")

    json_r = r.json()['rows']
    if len(json_r) != 1:
        if errors == 'ignore':
            return None
        else:
            raise Exception(f"Error ticket not found")

    ticket = json_r[0]
    return ticket


def get_key_stats_from_ticket(SecId: str, errors='ignore') -> dict:
    def parse_line(html_data: bs.element.Tag) -> dict:

        try:
            txt_heading = html_data.find('td', {'class': 'line heading'}).contents[0]
            txt_value = html_data.find('td', {'class': 'line text'}).contents[0]
        except AttributeError:
            return {'': ''}

        if 'Ongoing Charge' == txt_heading:
            # Ongoing Charge in percentage, removing % symbol
            return {'Charge': float(txt_value[:-1])}
        else:
            return {txt_heading.strip(): txt_value.strip()}

    url = f"https://www.morningstar.co.uk/uk/funds/snapshot/snapshot.aspx?id={SecId}"
    r = requests.get(url)
    if r.status_code != 200:
        if errors == 'ignore':
            return None
        else:
            raise Exception(f"Error, unexpected HTTP response code: {r.status_code} for secId: {SecId}")

    soup = bs.BeautifulSoup(r.text, "html.parser")
    try:
        html_data = soup.find("div", {'id': "overviewQuickstatsDiv"}).findAll("tr")
    except AttributeError:
        if errors == 'ignore':
            return None
        else:
            raise Exception(f"Error, couldn't find table for secId: {SecId}")

    rows = [parse_line(row) for row in html_data]
    ticket = dict(ChainMap(*rows))

    return ticket


def get_historical_data_from_ticket(ticket: dict,
                                    start_date: datetime.date, end_date: datetime.date = None,
                                    currency: str = None):
    security_id = ticket["SecId"]
    if currency is None:
        currency = ticket["PriceCurrency"]
    if end_date is None:
        end_date = datetime.date.today()
    start_date_str = dt.strftime(start_date, "%Y-%m-%d")
    end_date_str = dt.strftime(end_date, "%Y-%m-%d")

    url = f"https://tools.morningstar.es/api/rest.svc/timeseries_cumulativereturn/2nhcdckzon?id={security_id}&currencyId={currency}&frequency=daily&startDate={start_date_str}&endDate={end_date_str}&outputType=COMPACTJSON"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Error, unexpected HTTP response code: {r.status_code}")
    json_txt = f"""{{"columns":["date","value"], "data":{r.text} }}"""
    # Pandas is smart enough to convert the timestamp into date automatically because the column is called date
    df = pd.read_json(json_txt, orient='split')
    df.value = (df.value + 100)
    return df


class MorningStar(ValueInfo):
    tickets = {}

    def __init__(self, ISINs: list, currency: str = None, start_date: datetime.date = dt(2000, 1, 1)):
        self.currency = currency
        df_values = None
        if ISINs is not None:
            df_values = self.__get_historical_data_ISIN_list(ISINs, currency, start_date)
            if df_values is None:
                raise Exception("ERROR: No fund found!")
        ValueInfo.__init__(self, df_values)

    def _get_historical_data_from_ISIN(self, ISIN: str,
                                       start_date: datetime.date = dt(2018, 1, 1),
                                       currency: str = None) -> pd.DataFrame:
        for i in range(0, 3):
            ticket = get_ticket(ISIN)
            time.sleep(5)
            if ticket is not None:
                break

        if ticket is None:
            return None

        ticket_stats = get_key_stats_from_ticket(ticket["SecId"])
        if ticket_stats is not None:
            ticket['Charge'] = ticket_stats['Charge']
        else:
            ticket['Charge'] = 0

        self.tickets[ISIN] = ticket
        data = get_historical_data_from_ticket(ticket, start_date, currency=currency)
        return data.rename(columns={'value': ISIN}).set_index('date')

    def __get_historical_data_ISIN_list(self, ISINs: list,
                                        currency: str = None,
                                        start_date: datetime.date = dt(2000, 1, 1)):
        df_all = None
        for isin in ISINs:
            df = self._get_historical_data_from_ISIN(isin, currency=currency, start_date=start_date)
            if df_all is None:
                df_all = df
            elif df is not None:
                df_all = df_all.merge(df, on="date", how="outer")

        return df_all

    def calc_roi_var(self, num_days:float=365,  annual_charges_percentage: list=None):
        df_roi = self._calc_window_function(self.df_values, num_days, _roi)
        if annual_charges_percentage is None:
            annual_charges_percentage = [self.tickets[isin]['Charge'] / 100 * num_days / 365 for isin in df_roi.columns]

        df_charges = pd.DataFrame([annual_charges_percentage], columns=df_roi.columns).fillna(0)
        df_charges = pd.concat([df_charges] * df_roi.shape[0])

        self.df_roi = df_roi - df_charges.values

        self.df_var = self._calc_window_function(self.df_roi, num_days, np.nanvar)
        return self.df_roi, self.df_var

    def get_annual_charges(self):
        annual_charges_percentage = [self.tickets[isin]['Charge'] for isin in self.df_values.columns]
        return annual_charges_percentage