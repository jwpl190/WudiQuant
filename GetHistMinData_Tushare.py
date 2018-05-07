import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv
from pathlib import Path
from time import sleep

def calTimeDay(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')
# data_dir = "C:/KeLiQuant/"
# output_dir = "C:/KeLiQuant/StockHistData/"
data_dir = "C:/KeLiQuant/"
output_dir_5min = "C:/KeLiQuant/5_min_data/"
def getHistData():


    today = datetime.today().strftime('%Y-%m-%d')
    today = '2018-05-08'
    prev_n_days = calTimeDay(today, -10)  # make sure long enough to skip holidays
    stock_codes = pd.read_csv(data_dir + 'codeList.txt', dtype=str)['stock'].values
    # Get history minute prices
    ct = 0
    for stock in stock_codes:
            ct = ct +1
            # if ct<=1000:
            print (stock)
            try:
                price_data_df = ts.get_hist_data(stock, start=prev_n_days, end=today, ktype='5', retry_count=10,
                                                 pause=3)  # not including today's data
            except:
                print(stock, ' has not got data')
                continue
            if price_data_df is None:
                continue
            price_data_df.sort_index(inplace=True)

            #save to file
            filename = stock + "_5min"
            fullpath = output_dir_5min + filename
            price_data_df.to_csv(fullpath, index=True, columns=["close"])

    print(str(ct), ' stock have 5 min data from tushare')

def main():
    getHistData()



if __name__ == "__main__":main()
