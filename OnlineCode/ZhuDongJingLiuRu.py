import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import Config


def GetUpdatedList(Points, SampleList):
    res = []
    if len(Points) == 0:
        return SampleList

    for i in range(Points[0] + 1):
        res.append(SampleList[i])

    for i in range(len(Points) - 1):
        for index in range(Points[i] + 1, Points[i + 1] + 1):
            res.append(SampleList[index] + res[Points[i]])

    for i in range(Points[-1] + 1, len(SampleList)):
        res.append(SampleList[i] + res[Points[-1]])

    return res


def DrawChart_jingliuru(name, indexArray, instiList, label1, vipList, label2, midList, label3, indiList, label4,
                        timeArray, price_list):
    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(111)

    ## Get Split point
    Points = []
    for i in range(len(timeArray) - 1):
        time1 = timeArray[i]
        time2 = timeArray[i + 1]
        if (time1.day != time2.day):
            Points.append(i)

    instiList = GetUpdatedList(Points, instiList)
    vipList = GetUpdatedList(Points, vipList)
    midList = GetUpdatedList(Points, midList)
    indiList = GetUpdatedList(Points, indiList)

    print (instiList)
    print (vipList)
    print (midList)
    print (indiList)

    ax1.plot(indexArray, instiList, c='black', lw=2.5, label=label1)
    ax1.plot(indexArray, vipList, c='blue', lw=2.5, label=label2)
    ax1.plot(indexArray, midList, c='purple', lw=2.5, label=label3)
    ax1.plot(indexArray, indiList, c='orange', lw=2.5, label=label4)
    ax2 = ax1.twinx()
    ax2.plot(indexArray, price_list, '--', c='red', lw=2.5, label='gujia')
    interval = max(1, len(timeArray) / 10)
    interval = min(interval, 10)
    ax1.set_xticks(range(0, len(timeArray), int(interval)))
    ax1.set_xticklabels(timeArray[::int(interval)], rotation=90)

    ax1.grid(True)

    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc='upper left')

    ax1.set_title(name)
    plt.savefig(Config.PicPath)
    plt.close()


## Read from CSV
df = pd.read_csv(Config.CSVpath)

ClosingList = []
JiGouInflowList = []
DaHuInflowList = []
ZhongHuInflowList = []
SanHuInflowList = []
TimeList = []

for index, row in df.iterrows():
    # print(row)
    dt = datetime.strptime(df.loc[index, 'datetime'], "%Y-%m-%d %H:%M:%S")
    DATA_DATETIME = dt
    LAST_PRICE = df.loc[index, 'rt_last']

    rt_insti_inflow = df.loc[index, 'rt_insti_inflow']
    rt_vip_inflow = df.loc[index, 'rt_vip_inflow']
    rt_mid_inflow = df.loc[index, 'rt_mid_inflow']
    rt_indi_inflow = df.loc[index, 'rt_indi_inflow']

    ClosingList.append(LAST_PRICE)
    JiGouInflowList.append(rt_insti_inflow)
    DaHuInflowList.append(rt_vip_inflow)
    ZhongHuInflowList.append(rt_mid_inflow)
    SanHuInflowList.append(rt_indi_inflow)
    TimeList.append(DATA_DATETIME)

###### paint ########
timeArray = TimeList
indexArray = []
i = 0
while i < len(timeArray):
    indexArray.append(i)
    i = i + 1

DrawChart_jingliuru(Config.stockCode + ' Jing Liu Ru', indexArray, JiGouInflowList, 'ji gou jing liu ru',
                           DaHuInflowList, 'da hu jing liu ru',
                           ZhongHuInflowList, 'zhong hu jing liu ru', SanHuInflowList, 'san hu jing liu ru',
                           timeArray, ClosingList)

