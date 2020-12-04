import numpy as np
import pandas as pd

def _roi(x):
    return x[-1]/x[0]

def _calc_window_function(df_fund,num_days,func):

    df_fund=df_fund.set_index('date')
    df_fund = df_fund.sort_values(by='date',axis='index',ascending=True)
    cols = df_fund.columns[df_fund.columns!='date']

    df_w=pd.concat([df_fund[col].rolling(window=num_days).apply(_roi,raw=True) for col in cols],axis=1)
    df_w=df_w.dropna(how='all')
    return df_w


def calc_roi(df_fund, num_days=365):
    df_roi=_calc_window_function(df_fund,num_days,_roi)
    return df_roi

def calc_var(df_fund, num_days=365):
    pass

def calc_annual_return(df_fund):
    df_roi = calc_roi(df_fund)
    df_annual_roi=df_roi.groupby(df_roi.index.year).last()
    return df_annual_roi

def calc_annual_varianze(df_fund):
    df_roi = calc_roi(df_fund)
    df_annual_roi=df_roi.groupby(df_roi.index.year).var()
    return df_annual_roi

