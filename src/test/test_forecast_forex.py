from pyfunds import ForecastFX
import pytest

@pytest.mark.skip(reason="Web crawling not working")
def test_get_historical_data_from_ISIN():
    pred_fx = ForecastFX()
    df_pred = pred_fx.get_new_asset()
    assert df_pred.shape == (13, 8)
    assert df_pred.name[0] == "EURUSD"
    assert all(df_pred.bias_week.isin(['Bullish', 'Bearish', 'Neutral', 'Sideways']))

