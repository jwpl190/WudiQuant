import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import Config

def weimai(stockCode):
    ## Read from CSV
    df = pd.read_csv(Config.CSVpath)

    last_price_dic = {}
    rt_bsize_total_dic = {}
    rt_asize_total_dic = {}
    timeDic = {}

    for index, row in df.iterrows():
        DATA_DATETIME = datetime.strptime(df.loc[index, 'datetime'], "%Y-%m-%d")
        stock_code = df.loc[index, 'stock_code']
        LAST_PRICE = df.loc[index, 'rt_last']
        rt_bsize_total = df.loc[index, 'rt_bsize_total ']
        rt_asize_total = df.loc[index, 'rt_asize_total ']

        last_price_dic.setdefault(stock_code, []).append(LAST_PRICE)
        rt_bsize_total_dic.setdefault(stock_code,[]).append(rt_bsize_total)
        rt_asize_total_dic.setdefault(stock_code, []).append(rt_asize_total)

        timeDic.setdefault(stock_code,[]).append(DATA_DATETIME)

    timeArray = timeDic.get(stockCode)
    indexArray = []
    i = 0
    while i < len(timeArray):
        indexArray.append(i)
        i = i + 1
    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(111)
    ax1.plot(indexArray, rt_bsize_total_dic.get(stockCode), c='r', lw=2.5, label='WeiBuy')
    ax1.plot(indexArray, rt_asize_total_dic.get(stockCode), c='black', lw=2.5, label='WeiSell')
    ax2 = ax1.twinx()
    ax2.plot(indexArray, last_price_dic.get(stockCode), '--', c='blue', lw=2, label='gujia')

    interval=max(1,len(timeArray)/10)
    interval = min(interval,10)
    ax1.set_xticks(range(0, len(timeArray), int(interval)))
    ax1.set_xticklabels(timeArray[::int(interval)], rotation=90)

    ax1.grid(True)

    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc='upper left')

    ax1.set_title('WeimaiWeimai' + stockCode)
    plt.savefig(Config.PicPath)
    plt.close()

weimai(Config.stockCode)
