import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.finance as mpf


def CryptoData(symbol, frequency):
    #Params: String symbol, int frequency = 300,900,1800,7200,14400,86400
    #Returns: df from first available date
    url ='https://poloniex.com/public?command=returnChartData&currencyPair='+symbol+'&end=9999999999&period='+str(frequency)+'&start=0'
    df = pd.read_json(url)
    df.set_index('date',inplace=True)
    return df

df = CryptoData('USDT_BTC', 86400)

df = df.loc['2018-03-01':'2018-06-24']
df = df[::-1]
print (df)
