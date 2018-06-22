import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import Config


def ReplaceNone(arr):
    pre = 0
    for i in range(len(arr)):
        if not arr[i]:
            arr[i] = pre
        else:
            pre = arr[i]
    return arr

def HuGangTong(df):

    timeArray = []
    shhk_sh = []
    shhk_hk = []
    szhk_sz = []
    szhk_hk = []
    indexArray = []
    i=0

    for index, row in df.iterrows():
        # print(row)
        DATA_DATETIME = datetime.strptime(df.loc[index, 'datetime'], "%Y-%m-%d %H:%M:%S")
        shhk_sh.append(df.loc[index, 'shhk_sh'])
        shhk_hk.append(df.loc[index, 'shhk_hk'])
        szhk_sz.append(df.loc[index, 'szhk_sz'])
        szhk_hk.append(df.loc[index, 'szhk_hk'])
        timeArray.append(DATA_DATETIME)
        indexArray.append(i)
        i=i+1

    shhk_shData = np.cumsum(ReplaceNone(shhk_sh))
    shhk_hkData = np.cumsum(ReplaceNone(shhk_hk))
    szhk_szData = np.cumsum(ReplaceNone(szhk_sz))
    szhk_hkData = np.cumsum(ReplaceNone(szhk_hk))

    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(111)
    ax1.set_title("Hu Gang Tong")

    ax1.plot(indexArray, shhk_shData, c='black', lw=2, label='shhk_sh')
    ax1.plot(indexArray, shhk_hkData, c='blue', lw=2, label='shhk_hk')
    ax1.plot(indexArray, szhk_szData, c='r', lw=2, label='szhk_sz')
    ax1.plot(indexArray, szhk_hkData, c='orange', lw=2, label='szhk_hk')

    interval=max(1,len(timeArray)/10)
    interval = min(interval,10)
    ax1.set_xticks(range(0, len(timeArray), int(interval)))
    ax1.set_xticklabels(timeArray[::int(interval)], rotation=90)

    ax1.legend(loc='upper left')
    ax1.grid(True)

    plt.savefig(Config.PicPath)
    plt.close()


## Read from CSV
df = pd.read_csv(Config.CSVpath)
HuGangTong(df)