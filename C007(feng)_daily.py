import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv
def calTimeDate(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')

data_dir = "C:/KeLiQuant/"
output_dir = "C:/KeLiQuant/c007_output/"


today = datetime.today().strftime('%Y-%m-%d')
back_n_day = calTimeDate(today,-180)

today = '2018-05-04'

print ("today: " + today)
print ("back 180 day: " + back_n_day)

stock_codes = pd.read_csv(data_dir + 'codeList.txt',dtype=str)['stock'].values
res = []
for stock in stock_codes:

    #Get history prices
    price_data_df = ts.get_hist_data(stock,start=back_n_day,end=today,retry_count=10,pause=2)
    if price_data_df is None or len(price_data_df) == 0:
        continue
    price_data_df.sort_index(inplace=True)
    tushare_last_day = price_data_df.index.values[-1]
    if tushare_last_day != today:
        continue
    print(stock)
    prices_high = price_data_df['high'].values
    price_highest = max(prices_high)
    prices_low = price_data_df['low'].values
    prices_lowest = min(prices_low)



    if (price_highest - prices_lowest)/prices_lowest <=0.35:
        last_2wk = price_data_df[len(price_data_df)-5:]
        factor = 0
        for i in range(0,len(last_2wk)):
            factor = factor + (last_2wk['high'].values[i] - last_2wk['low'].values[i])
        factor = factor/len(last_2wk)/last_2wk['close'].values[-1]
        if factor > 0.03:
            print (stock,' has signal')
            res.append(stock)

filename = today + "_C007_output.csv"
fullpath = output_dir + filename

with open(fullpath, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for val in res:
        writer.writerow([val])



