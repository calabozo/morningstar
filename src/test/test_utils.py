import pytest
import pandas as pd
import numpy as np
from pyfunds.utils import calc_roi, calc_annual_return

@pytest.fixture
def df_fake():
    df_fake=pd.DataFrame({'date':pd.date_range(start='2010-01-07',end='2020-12-31',freq='D'),
                     'fund1':1.0001, 'fund2':30})
    df_fake['fund3']=np.random.normal(loc=15,scale=1,size=df_fake.shape[0])
    df_fake['fund4']=df_fake["fund1"].cumprod()    
    return df_fake


def test_roi(df_fake):
    df_roi=calc_roi(df_fake)
    assert df_fake.shape == (4012,5)
    assert df_roi.shape  == (4012-364,4)
    assert all(df_roi['fund1']==1)
    assert all(df_roi['fund2']==1)
    assert df_roi['fund3'].mean()<1.01
    assert df_roi['fund3'].var()>0
    assert pytest.approx(df_roi['fund4'].var(),1e-10)==0
    assert pytest.approx(df_roi.loc['2015-01-31','fund4'],0.01) == 1.037

def test_annual_return(df_fake):
    df_return=calc_annual_return(df_fake)
    assert all(df_return['fund1']==1)
    assert all(df_return['fund2']==1)
    assert df_return['fund3'].mean()>0.7
    assert df_return['fund3'].var()>0
    assert pytest.approx(df_return['fund4'].var(),1e-10)==0
    assert pytest.approx(df_return.loc[2015,'fund4'],0.01) == 1.037


