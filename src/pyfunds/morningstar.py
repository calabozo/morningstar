#!/usr/bin/python3
import requests
import json
import datetime
from datetime import datetime as dt
import pandas as pd


class MorningStar():
    def __init__(self):
        pass

    def get_ticket(self, ISIN: str, errors='ignore') -> dict:
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

    def get_historical_data_from_ticket(self, ticket: dict,
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
        # Pandas is smart enought to convert the timestamp into date automatically because the column is called date
        df = pd.read_json(json_txt, orient='split')
        return df

    def get_historical_data_from_ISIN(self, ISIN: str,
                                      start_date: datetime.date = dt(2018, 1, 1),
                                      currency: str = None) -> pd.DataFrame:
        ticket = self.get_ticket(ISIN)
        if ticket is None:
            return None

        data = self.get_historical_data_from_ticket(ticket, start_date, currency=currency)
        return data.rename(columns={'value': ISIN}).set_index('date')

    def get_historical_data_ISIN_list(self, ISINs: list,
                                      currency: str = None,
                                      start_date: datetime.date = dt(2018, 1, 1),
                                      save_to_disk_filename: str = None):
        df_all = None
        for isin in ISINs:
            df = self.get_historical_data_from_ISIN(isin, currency=currency, start_date=start_date)
            if df_all is None:
                df_all = df
            elif df is not None:
                df_all = df_all.merge(df, on="date", how="outer")

        if save_to_disk_filename is not None:
            self.save_to_disk(df_all, save_to_disk_filename)
        return df_all

    def save_to_disk(self, df_values, filename):
        return df_values.to_parquet(filename)

    def read_from_dist(self, filename):
        return pd.read_parquet(filename)


if __name__ == '__main__':
    funds = """
LU1328852659
LU1050470373
LU0389812933
LU0389811372
LU0996177134
LU0996176912
LU0389811885
LU0996180864
LU0390717543
LU0996182563
LU0996182308
LU0996179007
LU0996178884
LU1050469367
LU1050469441
LU1328852493
LU0389812347
ES0158967036
ES0110182039
ES0114105036
IE00BYX5M039
IE00BYX5ML46
IE00BYX5MD61
IE00BYX5NH74
IE00BYX5P602
IE00BYX5NX33
IE00BYX5NK04
IE00BYX5N110
IE00BYX5MX67
IE00BYX5MS15
ES0149051007
IE00BYWYCC39
ES0148181003
IE0007471471
IE00B246KL88
IE0031786142
IE0032125126
IE0007472115
IE00B04FFJ44
IE0009591805
IE0007987690
IE0002639551
IE00B04GQQ17
IE00B04GQR24
IE0008248795
IE00B18GC888
IE00BGCZ0826
IE00BH65QK91
IE00BH65QN23
IE00B42LF923
IE00B42W3S00
IE00B03HCZ61
IE00B03HD084
IE0007281425
IE0007292083
IE0007218849
IE0007201266
IE0007201043
IE0032620787
IE0002639668
IE0007471695
IE00B04GQT48
IE00B04GQX83
IE00B89M2V73
IE00B83YJG36
IE00BD0NCM55
IE00BD0NCN62
IE00B62C5H76
IE00B3B2KS38
LU1373035580
LU0836513696
IE00B3D07F16
IE00B3D07G23
LU0836513423
LU0836513266
IE00B4K9F548
LU0836513852
IE00BDRK7T12
IE00B6RVWW34
IE00B1W56M32
IE00BDRK7R97
IE00B56H2V49
IE00B1W56S93
IE00BDZS0987
IE00BDFVDR63
IE00B1W56J03
IE00B4XCK338
"""
