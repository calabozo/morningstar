import pandas as pd
import numpy as np


def _roi(x):
    return x[-1] / x[0]


class ValueInfo:
    df_values = None
    df_roi = None
    df_var = None

    def __init__(self, df_values):
        self.df_values = df_values
        pass

    def save_to_disk(self, filename):
        return self.df_values.to_parquet(filename)

    def read_from_dist(self, filename):
        self.df_values = pd.read_parquet(filename)

    def _calc_window_function(self, df, num_days, func):
        df_fund = df.sort_values(by='date', axis='index', ascending=True)

        df_w = df_fund.rolling(window=f"{num_days}D").apply(func, raw=True)
        df_w = df_w[df_w.index >= df_fund.index[0] + pd.Timedelta(num_days - 1, unit='D')]. \
            replace([np.inf, -np.inf], np.nan).dropna(how='all')
        return df_w

    def calc_roi_var(self, num_days=365, annual_charges_percentage=0):
        charges = annual_charges_percentage * num_days / 365 /100
        self.df_roi = self._calc_window_function(self.df_values, num_days, _roi)
        self.df_roi = self.df_roi - charges

        self.df_var = self._calc_window_function(self.df_roi, num_days, np.nanvar)
        return self.df_roi, self.df_var

    def calc_annual_return(self):
        df_roi, _ = self.calc_roi_var(365)
        df_annual_roi = df_roi.groupby(df_roi.index.year).last()
        return df_annual_roi

    def calc_annual_var(self, period_days=2):
        df_roi, _ = self.calc_roi_var(period_days)
        df_annual_roi = df_roi.groupby(df_roi.index.year).var()
        return df_annual_roi

    def _sort(self):
        self.df_values = self.df_values.sort_values(by='date', axis='index', ascending=True)

    def get_data(self, cols: list = None, max_date=None):
        if max_date is None:
            out = self.df_values
        else:
            out = self.df_values[self.df_values.index <= max_date]
        if cols is None:
            return out
        else:
            return out[cols]
