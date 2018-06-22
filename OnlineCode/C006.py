import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import Config

def DrawChart(percent, indexArray, upList, downList, timeArray, index_list, up_10_list, down_10_list):
    fig = plt.figure(figsize=(20,10))
    ax1 = fig.add_subplot(111)
    ax1.plot(indexArray, upList, c='r', lw=2.5, label='up')
    ax1.plot(indexArray, downList, c='black', lw=2.5, label='down')

    ax1.plot(indexArray, up_10_list, ':', c='r', lw=2.5, label='ZhangTing')
    ax1.plot(indexArray, down_10_list, ':', c='black', lw=2.5, label='DieTing')

    ax2 = ax1.twinx()
    ax2.plot(indexArray, index_list, '--', c='blue', lw=2, label='Dapan')

    interval=max(1,len(timeArray)/10)
    interval = min(interval,10)
    ax1.set_xticks(range(0, len(timeArray), int(interval)))
    ax1.set_xticklabels(timeArray[::int(interval)], rotation=90)

    ax1.grid(True)

    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc='upper left')
    ax1.set_title('number of stocks which up/down' + percent)

    plt.savefig(Config.PicPath)
    plt.close()

def C006AllPaint(startTime, endTime, option, df):

    index_list = []
    up_5_list = []
    down_5_list = []
    up_4_list = []
    down_4_list = []
    up_3_list = []
    down_3_list = []
    up_2_list = []
    down_2_list = []
    up_10_list = []
    down_10_list = []
    timeArray = []
    indexArray = []
    i = 0

    up_5 = 0;
    down_5 = 0;
    up_4 = 0;
    down_4 = 0;
    up_3 = 0;
    down_3 = 0;
    up_2 = 0;
    down_2 = 0

    for index, row in df.iterrows():
        dt = datetime.strptime(df.loc[index, 'DATA_DATETIME'], "%Y-%m-%d %H:%M:%S")
        index = df.loc[index, 'CUR_INDEX']
        up_5 = df.loc[index, 'UP_5']
        down_5 = df.loc[index, 'DOWN_5']
        up_4 = df.loc[index, 'UP_4']
        down_4 = df.loc[index, 'DOWN_4']
        up_3 = df.loc[index, 'UP_3']
        down_3 = df.loc[index, 'DOWN_3']
        up_2 = df.loc[index, 'UP_2']
        down_2 = df.loc[index, 'DOWN_2']
        up_10 = df.loc[index, 'UP_10']
        down_10 = df.loc[index, 'DOWN_10']

        timeArray.append(dt)
        indexArray.append(i)
        i = i + 1
        index_list.append(index)
        up_5_list.append(up_5)
        down_5_list.append(down_5)
        up_4_list.append(up_4)
        down_4_list.append(down_4)
        up_3_list.append(up_3)
        down_3_list.append(down_3)
        up_2_list.append(up_2)
        down_2_list.append(down_2)
        up_10_list.append(up_10)
        down_10_list.append(down_10)


    ###### paint ########
    if option == 5:
        print (down_5_list)
        return DrawChart('5%', indexArray, up_5_list, down_5_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 4:
        return DrawChart('4%', indexArray, up_4_list, down_4_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 3:
        return DrawChart('3%', indexArray, up_3_list, down_3_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 2:
        return DrawChart('2%', indexArray, up_2_list, down_2_list, timeArray, index_list, up_10_list, down_10_list)

def C006HuAPaint(startTime, endTime, option, df):

    index_list = []
    up_5_list = []
    down_5_list = []
    up_4_list = []
    down_4_list = []
    up_3_list = []
    down_3_list = []
    up_2_list = []
    down_2_list = []
    up_10_list = []
    down_10_list = []
    timeArray = []
    indexArray = []
    i = 0

    up_5 = 0;
    down_5 = 0;
    up_4 = 0;
    down_4 = 0;
    up_3 = 0;
    down_3 = 0;
    up_2 = 0;
    down_2 = 0

    for index, row in df.iterrows():
        dt = datetime.strptime(df.loc[index, 'DATA_DATETIME'], "%Y-%m-%d %H:%M:%S")
        index = df.loc[index, 'CUR_INDEX']
        up_5 = df.loc[index, 'UP_HUA_5']
        down_5 = df.loc[index, 'DOWN_HUA_5']
        up_4 = df.loc[index, 'UP_HUA_4']
        down_4 = df.loc[index, 'DOWN_HUA_4']
        up_3 = df.loc[index, 'UP_HUA_3']
        down_3 = df.loc[index, 'DOWN_HUA_3']
        up_2 = df.loc[index, 'UP_HUA_2']
        down_2 = df.loc[index, 'DOWN_HUA_2']
        up_10 = df.loc[index, 'UP_HUA_10']
        down_10 = df.loc[index, 'DOWN_HUA_10']

        timeArray.append(dt)
        indexArray.append(i)
        i = i + 1
        index_list.append(index)
        up_5_list.append(up_5)
        down_5_list.append(down_5)
        up_4_list.append(up_4)
        down_4_list.append(down_4)
        up_3_list.append(up_3)
        down_3_list.append(down_3)
        up_2_list.append(up_2)
        down_2_list.append(down_2)
        up_10_list.append(up_10)
        down_10_list.append(down_10)


    ###### paint ########
    if option == 5:
        print (down_5_list)
        return DrawChart('5%', indexArray, up_5_list, down_5_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 4:
        return DrawChart('4%', indexArray, up_4_list, down_4_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 3:
        return DrawChart('3%', indexArray, up_3_list, down_3_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 2:
        return DrawChart('2%', indexArray, up_2_list, down_2_list, timeArray, index_list, up_10_list, down_10_list)

def C006ShenAPaint(startTime, endTime, option, df):
    conn = mysql.connector.connect(**config)
    conn.set_converter_class(NumpyMySQLConverter)

    index_list = []
    up_5_list = []
    down_5_list = []
    up_4_list = []
    down_4_list = []
    up_3_list = []
    down_3_list = []
    up_2_list = []
    down_2_list = []
    up_10_list = []
    down_10_list = []
    timeArray = []
    indexArray = []
    i = 0

    up_5 = 0;
    down_5 = 0;
    up_4 = 0;
    down_4 = 0;
    up_3 = 0;
    down_3 = 0;
    up_2 = 0;
    down_2 = 0

    for index, row in df.iterrows():
        dt = datetime.strptime(df.loc[index, 'DATA_DATETIME'], "%Y-%m-%d %H:%M:%S")
        index = df.loc[index, 'SZ_INDEX']
        up_5 = df.loc[index, 'UP_SHA_5']
        down_5 = df.loc[index, 'DOWN_SHA_5']
        up_4 = df.loc[index, 'UP_SHA_4']
        down_4 = df.loc[index, 'DOWN_SHA_4']
        up_3 = df.loc[index, 'UP_SHA_3']
        down_3 = df.loc[index, 'DOWN_SHA_3']
        up_2 = df.loc[index, 'UP_SHA_2']
        down_2 = df.loc[index, 'DOWN_SHA_2']
        up_10 = df.loc[index, 'UP_SHA_10']
        down_10 = df.loc[index, 'DOWN_SHA_10']

        timeArray.append(dt)
        indexArray.append(i)
        i = i + 1
        index_list.append(index)
        up_5_list.append(up_5)
        down_5_list.append(down_5)
        up_4_list.append(up_4)
        down_4_list.append(down_4)
        up_3_list.append(up_3)
        down_3_list.append(down_3)
        up_2_list.append(up_2)
        down_2_list.append(down_2)
        up_10_list.append(up_10)
        down_10_list.append(down_10)


    ###### paint ########
    if option == 5:
        print (down_5_list)
        return DrawChart('5%', indexArray, up_5_list, down_5_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 4:
        return DrawChart('4%', indexArray, up_4_list, down_4_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 3:
        return DrawChart('3%', indexArray, up_3_list, down_3_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 2:
        return DrawChart('2%', indexArray, up_2_list, down_2_list, timeArray, index_list, up_10_list, down_10_list)

def C006ChuangYePaint(startTime, endTime, option, df):
    index_list = []
    up_5_list = []
    down_5_list = []
    up_4_list = []
    down_4_list = []
    up_3_list = []
    down_3_list = []
    up_2_list = []
    down_2_list = []
    up_10_list = []
    down_10_list = []
    timeArray = []
    indexArray = []
    i = 0

    up_5 = 0;
    down_5 = 0;
    up_4 = 0;
    down_4 = 0;
    up_3 = 0;
    down_3 = 0;
    up_2 = 0;
    down_2 = 0

    for index, row in df.iterrows():
        dt = datetime.strptime(df.loc[index, 'DATA_DATETIME'], "%Y-%m-%d %H:%M:%S")
        index = df.loc[index, 'CY_INDEX']
        up_5 = df.loc[index, 'UP_CHUANGYE_5']
        down_5 = df.loc[index, 'DOWN_CHUANGYE_5']
        up_4 = df.loc[index, 'UP_CHUANGYE_4']
        down_4 = df.loc[index, 'DOWN_CHUANGYE_4']
        up_3 = df.loc[index, 'UP_CHUANGYE_3']
        down_3 = df.loc[index, 'DOWN_CHUANGYE_3']
        up_2 = df.loc[index, 'UP_CHUANGYE_2']
        down_2 = df.loc[index, 'DOWN_CHUANGYE_2']
        up_10 = df.loc[index, 'UP_CHUANGYE_10']
        down_10 = df.loc[index, 'DOWN_CHUANGYE_10']

        timeArray.append(dt)
        indexArray.append(i)
        i = i + 1
        index_list.append(index)
        up_5_list.append(up_5)
        down_5_list.append(down_5)
        up_4_list.append(up_4)
        down_4_list.append(down_4)
        up_3_list.append(up_3)
        down_3_list.append(down_3)
        up_2_list.append(up_2)
        down_2_list.append(down_2)
        up_10_list.append(up_10)
        down_10_list.append(down_10)


    ###### paint ########
    if option == 5:
        print (down_5_list)
        return DrawChart('5%', indexArray, up_5_list, down_5_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 4:
        return DrawChart('4%', indexArray, up_4_list, down_4_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 3:
        return DrawChart('3%', indexArray, up_3_list, down_3_list, timeArray, index_list, up_10_list, down_10_list)

    if option == 2:
        return DrawChart('2%', indexArray, up_2_list, down_2_list, timeArray, index_list, up_10_list, down_10_list)

## Read from CSV
df = pd.read_csv(Config.CSVpath)
C006AllPaint(Config.startTime, Config.endTime, Config.option, df)
C006HuAPaint(Config.startTime, Config.endTime, Config.option, df)
C006ShenAPaint(Config.startTime, Config.endTime, Config.option, df)
C006ChuangYePaint(Config.startTime, Config.endTime, Config.option, df)