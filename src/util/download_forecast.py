from pyfunds import ForecastFX

def main():
    pred_fx = ForecastFX("forecast_forex.csv")
    pred_fx.get_new_asset()
    pred_fx.save()


if __name__ == "__main__":
    # execute only if run as a script
    main()