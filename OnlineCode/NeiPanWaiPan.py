import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import Config

## Read from CSV
df = pd.read_csv(Config.CSVpath)

closingList = []
downwardList = []
upwardList = []
timeList = []
stock_code = Config.stockCode

for index, row in df.iterrows():
    DATA_DATETIME = datetime.strptime(df.loc[index, 'datetime'], "%Y-%m-%d %H:%M:%S")
    LAST_PRICE = df.loc[index, 'rt_last']
    downward_vol = df.loc[index, 'rt_downward_vol']
    upward_vol = df.loc[index, 'rt_upward_vol']
    closingList.append(LAST_PRICE)
    downwardList.append(downward_vol)
    upwardList.append(upward_vol)
    timeList.append(DATA_DATETIME)

indexArray = []
i = 0
while i < len(timeList):
    indexArray.append(i)
    i = i + 1

fig = plt.figure(figsize=(20, 10))
ax1 = fig.add_subplot(111)
ax1.plot(indexArray, downwardList, c='r', lw=2.5, label='downward')
ax1.plot(indexArray, upwardList, c='black', lw=2.5, label='upward')
ax2 = ax1.twinx()
ax2.plot(indexArray, closingList, '--', c='blue', lw=2, label='GuJia')

interval = max(1, len(timeList) / 10)
interval = min(interval, 10)
ax1.set_xticks(range(0, len(timeList), int(interval)))
ax1.set_xticklabels(timeList[::int(interval)], rotation=90)

ax1.grid(True)

lines = ax1.get_lines() + ax2.get_lines()
ax1.legend(lines, [line.get_label() for line in lines], loc='upper left')

ax1.set_title('NeiPanWaiPan ' + Config.stockCode)
plt.savefig(Config.PicPath + "-NeiPanWaiPan" + '.png')
plt.close()
