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


def DrawChart_zhudongmaimai(name, indexArray, instiBuyList, vipBuyList, midBuyList, indiBuyList,
                            instiSellList, vipSellList,
                            midSellList, indiSellList,
                            timeArray, price_list):
    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(111)
    ## Zhu Dong MAi Mai tu, split two bars
    instiSellList_Neg = [-x for x in instiSellList]
    ax1.bar(indexArray, instiBuyList, 0.5, color='pink', label='Ji Gou Mai Ru')
    ax1.bar(indexArray, instiSellList_Neg, 0.5, color='deepskyblue', label='Ji Gou Mai Chu')

    sub_insti = list(np.array(instiBuyList) - np.array(instiSellList))
    sub_vip = list(np.array(vipBuyList) - np.array(vipSellList))
    sub_mid = list(np.array(midBuyList) - np.array(midSellList))
    sub_indi = list(np.array(indiBuyList) - np.array(indiSellList))

    ## Get Split point
    Points = []
    for i in range(len(timeArray) - 1):
        time1 = timeArray[i]
        time2 = timeArray[i + 1]

        if (time1.day != time2.day):
            Points.append(i)

    sub_insti = GetUpdatedList(Points, sub_insti)
    sub_vip = GetUpdatedList(Points, sub_vip)
    sub_mid = GetUpdatedList(Points, sub_mid)
    sub_indi = GetUpdatedList(Points, sub_indi)

    ax1.plot(indexArray, sub_insti, c='black', lw=2.5, label='diff insti')
    ax1.plot(indexArray, sub_vip, c='blue', lw=2.5, label='diff vip')
    ax1.plot(indexArray, sub_mid, c='purple', lw=2.5, label='diff mid')
    ax1.plot(indexArray, sub_indi, c='orange', lw=2.5, label='diff indi')

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
    plt.savefig(plt.savefig(Config.PicPath + "-ZhuDongMaiMai" + '.png'))
    plt.close()



## Read from CSV
df = pd.read_csv(Config.CSVpath)

closingList = []
JiGouMaiRuList = []
DaHuMaiRuList = []
ZhongHuMaiRuList = []
SanHuMaiRuList = []
JiGouMaiChuList = []
DaHuMaiChuList = []
ZhongHuMaiChuList = []
SanHuMaiChuList = []
TimeList = []

for index, row in df.iterrows():

    # print(row)
    dt = datetime.strptime(df.loc[index, 'datetime'], "%Y-%m-%d %H:%M:%S")
    DATA_DATETIME = dt
    LAST_PRICE = df.loc[index, 'rt_last']
    rt_insti_activebuy_amt = df.loc[index, 'rt_insti_activebuy_amt']
    rt_vip_activebuy_amt = df.loc[index, 'rt_vip_activebuy_amt']
    rt_mid_activebuy_amt = df.loc[index, 'rt_mid_activebuy_amt']
    rt_indi_activebuy_amt = df.loc[index, 'rt_indi_activebuy_amt']
    rt_insti_activesell_amt = df.loc[index, 'rt_insti_activesell_amt']
    rt_vip_activesell_amt = df.loc[index, 'rt_vip_activesell_amt']
    rt_mid_activesell_amt = df.loc[index, 'rt_mid_activesell_amt']
    rt_indi_activesell_amt = df.loc[index, 'rt_indi_activesell_amt']

    closingList.append(LAST_PRICE)
    JiGouMaiRuList.append(rt_insti_activebuy_amt)
    DaHuMaiRuList.append(rt_vip_activebuy_amt)
    ZhongHuMaiRuList.append(rt_mid_activebuy_amt)
    SanHuMaiRuList.append(rt_indi_activebuy_amt)
    JiGouMaiChuList.append(rt_insti_activesell_amt)
    DaHuMaiChuList.append(rt_vip_activesell_amt)
    ZhongHuMaiChuList.append(rt_mid_activesell_amt)
    SanHuMaiChuList.append(rt_indi_activesell_amt)
    TimeList.append(DATA_DATETIME)


###### paint ########
timeArray = TimeList
indexArray = []
i = 0
while i < len(timeArray):
    indexArray.append(i)
    i = i + 1

DrawChart_zhudongmaimai(Config.stockCode +' ZhuDongMaiMai', indexArray, JiGouMaiRuList,
                               DaHuMaiRuList, ZhongHuMaiRuList,
                               SanHuMaiRuList, JiGouMaiChuList,
                               DaHuMaiChuList, ZhongHuMaiChuList,
                               SanHuMaiChuList, timeArray, closingList)

