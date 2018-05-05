import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv
from pathlib import Path
from time import sleep
def calTimeDate(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')

data_dir = "C:/KeLiQuant/"
output_dir = "C:/KeLiQuant/StockHistData/"

def getHistData():
    today = datetime.today().strftime('%Y-%m-%d')
    today = '2018-04-27'

    back_n_day = calTimeDate(today, -50)

    print("today: " + today)
    print("back  day: " + back_n_day)

    stock_codes = pd.read_csv(data_dir + 'codeList.txt', dtype=str)['stock'].values
    res = []
    for stock in stock_codes:

        # Get history prices
        price_data_df = ts.get_hist_data(stock, start=back_n_day, end=today, retry_count=10, pause=2)
        if price_data_df is None or len(price_data_df) == 0:
            continue
        price_data_df.sort_index(inplace=True)
        tushare_last_day = price_data_df.index.values[-1]
        if tushare_last_day != today:
            continue
        print(stock)
        filename = output_dir + stock + '_hist'
        if not Path(filename).is_file():
            header = 'date,high,low'
            fd = open(filename, 'a')
            fd.write(header)
            fd.write('\n')
            fd.close()
        price_data_df.to_csv(filename, index=True, columns=['high', 'low'], header=False, mode='a')

def updateHistData():
    while (1):
        weekno = datetime.today().weekday()
        if weekno in [0, 1, 2, 3, 4]:
            dateTime = datetime.today().strftime('%Y-%m-%d %H-%M')
            curDate = dateTime.split(' ')[0]
            curTime = dateTime.split(' ')[1]

            if curTime == '20-00':
                stock_codes = pd.read_csv(data_dir + 'codeList.txt', dtype=str)['stock'].values
                for stock in stock_codes:

                    # Get history prices
                    price_data_df = ts.get_hist_data(stock, start=curDate, end=curDate, retry_count=10, pause=2)
                    if price_data_df is None or len(price_data_df) == 0:
                        continue
                    price_data_df.sort_index(inplace=True)
                    tushare_last_day = price_data_df.index.values[-1]
                    if tushare_last_day != curDate:
                        continue
                    print(stock)
                    filename = output_dir + stock + '_hist'
                    if not Path(filename).is_file():
                        header = 'date,high,low'
                        fd = open(filename, 'a')
                        fd.write(header)
                        fd.write('\n')
                        fd.close()
                    price_data_df.to_csv(filename, index=True, columns=['high', 'low'], header=False, mode='a')
                print ('done')

        sleep(60)
def main():
    #1st time run -- get certain days data
    # getHistData()
    #update file with latest high, low
    updateHistData()



if __name__ == "__main__":main()
