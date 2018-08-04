import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import Config

def weimai():
    ## Read from CSV
    df = pd.read_csv(Config.CSVpath)

    last_price_dic = []
    rt_bsize_total_dic = []
    rt_asize_total_dic = []
    timeDic = []

    for index, row in df.iterrows():
        dt = datetime.strptime(df.loc[index, 'datetime'], "%Y-%m-%d %H:%M:%S")
        LAST_PRICE = df.loc[index, 'rt_last']
        rt_bsize_total = df.loc[index, 'rt_bsize_total ']
        rt_asize_total = df.loc[index, 'rt_asize_total']

        last_price_dic.append(LAST_PRICE)
        rt_bsize_total_dic.append(rt_bsize_total)
        rt_asize_total_dic.append(rt_asize_total)

        timeDic.append(dt)


    indexArray = []
    i = 0
    while i < len(timeDic):
        indexArray.append(i)
        i = i + 1
    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(111)
    ax1.plot(indexArray, rt_bsize_total_dic, c='r', lw=2.5, label='WeiBuy')
    ax1.plot(indexArray, rt_asize_total_dic, c='black', lw=2.5, label='WeiSell')
    ax2 = ax1.twinx()
    ax2.plot(indexArray, last_price_dic, '--', c='blue', lw=2, label='gujia')

    interval=max(1,len(timeDic)/10)
    interval = min(interval,10)
    ax1.set_xticks(range(0, len(timeDic), int(interval)))
    ax1.set_xticklabels(timeDic[::int(interval)], rotation=90)

    ax1.grid(True)

    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc='upper left')

    ax1.set_title('WeimaiWeimai' + Config.stockCode)
    plt.savefig(Config.PicPath + "-WeiMaiWeiMai" + '.png')
    plt.close()

weimai()
