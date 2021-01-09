from yahoo_finance import Currency
from .valueinfo import ValueInfo
import requests
from bs4 import BeautifulSoup
import io
import zipfile
import pandas as pd

#TODO: https://www.histdata.com/download-free-forex-data/
"""
EUR/USD, EUR/CHF, EUR/GBP, EUR/JPY, EUR/AUD, USD/CAD, USD/CHF, USD/JPY, USD/MXN, GBP/CHF, GBP/JPY, GBP/USD, AUD/JPY, AUD/USD, CHF/JPY, NZD/JPY, NZD/USD, XAU/USD, EUR/CAD, AUD/CAD, CAD/JPY, EUR/NZD, GRX/EUR, NZD/CAD, SGD/JPY, USD/HKD, USD/NOK, USD/TRY, XAU/AUD, AUD/CHF, AUX/AUD, EUR/HUF, EUR/PLN, FRX/EUR, HKX/HKD, NZD/CHF, SPX/USD, USD/HUF, USD/PLN, USD/ZAR, XAU/CHF, ZAR/JPY, BCO/USD, ETX/EUR, EUR/CZK, EUR/SEK, GBP/AUD, GBP/NZD, JPX/JPY, UDX/USD, USD/CZK, USD/SEK, WTI/USD, XAU/EUR, AUD/NZD, CAD/CHF, EUR/DKK, EUR/NOK, EUR/TRY, GBP/CAD, NSX/USD, UKX/GBP, USD/DKK, USD/SGD, XAG/USD, XAU/GBP
"""
class Forex(ValueInfo):
    pair=""
    base_url = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes"

    def __init__(self,fxpair):
        self.fxpair = fxpair
        pass

    def _get_token(self,year,month):
        url=f"{self.base_url}/{self.fxpair}/{year}/{month}"
        page = requests.get(url)
        if page.status_code != 200:
            return None
        soup = BeautifulSoup(page.content, 'html.parser')
        token = soup.find('form', {'id': 'file_down'}).find("input", {'id': 'tk'}).get_attribute_list("value")[0]
        return token

    def _get_month(self, year, month, token):
        data = {'tk': token,
                'date': year,
                'datemonth':f'{year}{month}',
                'platform':'ASCII',
                'timeframe':'M1',
                'fxpair':self.fxpair.upper()
                }
        headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7,ca;q=0.6',
'Cookie': 'cookielawinfo-checkbox-non-necessary=yes; viewed_cookie_policy=yes',
'Referer': f"{self.base_url}/{self.fxpair}/{year}/{month}",
'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
'sec-ch-ua-mobile': '?0',
'Sec-Fetch-Dest': 'iframe',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'same-origin',
'Sec-Fetch-User': '?1',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        }
        page = requests.post("https://www.histdata.com/get.php",data=data, headers=headers)
        zipdata = io.BytesIO(page.content)
        unzipped_data = zipfile.ZipFile(zipdata)
        files = unzipped_data.namelist()
        csv_filename = None
        for f in files:
            if f.endswith(".csv"):
                csv_filename=f

        csv_file = unzipped_data.open(csv_filename)
        df_forex = pd.read_csv(csv_file, sep=";", names=["date", "open", "high", "low", "close", "none"])
        df_forex = df_forex.drop(columns=["none"])
        #TODO: parse date
        return df_forex
