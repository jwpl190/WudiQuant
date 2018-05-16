from WindPy import *
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import mysql.connector
import math
import requests
import tushare as ts
import talib
import numpy as np
import os
from pathlib import Path
# Run at US morning



def getAllStockList():
    allStock = w.wset("sectorconstituent", "sectorid=a001010100000000;field=wind_code")
    fm = pd.DataFrame(allStock.Data, index=allStock.Fields)
    fm = fm.T  # Transpose index and columns
    code_list = fm['wind_code'].values
    return code_list


def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes


def conWSQData(indata1):
    fm = pd.DataFrame(indata1.Data, index=indata1.Fields, columns=indata1.Codes)
    fm = fm.T  # Transpose index and columns
    fm['code'] = fm.index
    fm['datetime'] = indata1.Times[0]
    return fm


def conWSDData(data):
    fm = pd.DataFrame(data.Data, index=data.Fields, columns=data.Times)
    fm = fm.T  # Transpose index and columns
    return fm


def getTDays(offset, date):  ##Get trading date with offset####
    date_data = w.tdaysoffset(offset, date, "")
    date = date_data.Data[0][0]
    return date.strftime('%Y-%m-%d')


def calTimeDay(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')


def calTimeHour(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d %H-%M') + timedelta(hours=delta)).strftime(
        '%Y-%m-%d %H-%M')

def calTimeHourWind(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=delta)).strftime(
        '%Y-%m-%d %H:%M:%S')

def checkMACDSignal(macds):
    # if len(macds) < 5:
    #     return False
    if len(macds) < 2:
        return False
    # print (macds)
    flag = False
    # if macds[-5] < 0 and macds[-4] < 0 and macds[-3] < 0 and macds[-2] < 0 and macds[-1] < 0 and \
    #                 macds[-5] > macds[-4] and macds[-4] > macds[-3] and macds[-3] > macds[
    #     -2] and macds[-2] < macds[-1]:
    #     flag = True

    #last MACD is larger than previous one
    if macds[-2] < macds[-1]:
        flag = True
    return flag


########################################################################################################
day_price = []
min_30_price = {}
min_60_price = {}
min_5_price = {}

min_30_macd = {}
min_60_macd = {}
min_5_macd = {}

day_macd = {}
#
data_dir = "C:/KeLiQuant/"
output_dir_30 = "C:/KeLiQuant/30_min_data/"
output_dir_60 = "C:/KeLiQuant/60_min_data/"
output_dir_5 = "C:/KeLiQuant/5_min_data/"
output_dir_histdata = "C:/KeLiQuant/StockHistData/"
############################################Get from Tushare#################################################################
# today = datetime.today().strftime('%Y-%m-%d')
# today = '2018-04-21'#This is CN today, US next day
# prev_n_days = calTimeDay(today, -25)  # make sure long enough to skip holidays
# stock_codes = pd.read_csv(data_dir + 'codeList.txt', dtype=str)['stock'].values
# # Get history minute prices
# ct = 0
# for stock in stock_codes:
#         # ct = ct +1
#         # if ct<=1000:
#             print (stock)
#             try:
#                 price_data_df = ts.get_hist_data(stock, start=prev_n_days, end=today, ktype='30', retry_count=10,
#                                                  pause=3)  # not including today's data
#             except:
#                 print(stock, ' has not got data')
#                 continue
#             if price_data_df is None:
#                 continue
#             price_data_df.sort_index(inplace=True)
#
#             #save to file
#             filename = stock + "_30min"
#             fullpath = output_dir_30 + filename
#             price_data_df.to_csv(fullpath, index=True, columns=["close"])
#
#             min_30_price[stock] = list(price_data_df['close'].values)
#
#             try:
#                 price_data_df = ts.get_hist_data(stock, start=prev_n_days, end=today, ktype='60', retry_count=10,
#                                                  pause=3)  # not including today's data
#             except:
#                 print(stock, ' has not got data')
#             if price_data_df is None:
#                 continue
#             price_data_df.sort_index(inplace=True)
#
#             #save to file
#             filename = stock + "_60min"
#             fullpath = output_dir_60 + filename
#             price_data_df.to_csv(fullpath, index=True, columns=["close"])
#
#             min_60_price[stock] = list(price_data_df['close'].values)
# print(str(len(min_30_price)), ' stock have 30/60 min data from tushare')
###########################################################################################################################

#################################Read history price from files############################################################
for root, dirs, files in os.walk(output_dir_30):
    for file in files:
        stock = file.split('_')[0]
        # print (stock)
        try:
            min_30_price[stock] = pd.read_csv(output_dir_30 + file, dtype=str)['close'].values
        except:
            print (file)
        min_30_price[stock] = [float(x) for x in min_30_price[stock]]
for root, dirs, files in os.walk(output_dir_60):
    for file in files:
        stock = file.split('_')[0]
        # print (stock)
        min_60_price[stock] = pd.read_csv(output_dir_60 + file, dtype=str)['close'].values
        min_60_price[stock] = [float(x) for x in min_60_price[stock]]

for root, dirs, files in os.walk(output_dir_5):
    for file in files:
        stock = file.split('_')[0]
        # print (stock)
        min_5_price[stock] = pd.read_csv(output_dir_5 + file, dtype=str)['close'].values
        min_5_price[stock] = [float(x) for x in min_5_price[stock]]

for stock in min_30_price.keys():
    if len(min_30_price)>0:
        try:
            macds = talib.MACD(np.asarray(min_30_price[stock]), 12, 26, 9)[2]
            min_30_macd.setdefault(stock, []).append(macds[-5] *2)
            min_30_macd.setdefault(stock, []).append(macds[-4] *2)
            min_30_macd.setdefault(stock, []).append(macds[-3] *2)
            min_30_macd.setdefault(stock, []).append(macds[-2] *2)
            min_30_macd.setdefault(stock, []).append(macds[-1] *2)
        except:
            continue
for stock in min_60_price.keys():
    if len(min_60_price)>0:
        try:
            macds = talib.MACD(np.asarray(min_60_price[stock]), 12, 26, 9)[2]
            min_60_macd.setdefault(stock, []).append(macds[-5] *2)
            min_60_macd.setdefault(stock, []).append(macds[-4] *2)
            min_60_macd.setdefault(stock, []).append(macds[-3] *2)
            min_60_macd.setdefault(stock, []).append(macds[-2] *2)
            min_60_macd.setdefault(stock, []).append(macds[-1] *2)
        except:
            continue
for stock in min_5_price.keys():
    if len(min_5_price) > 0:
        try:
            macds = talib.MACD(np.asarray(min_5_price[stock]), 12, 26, 9)[2]
            min_5_macd.setdefault(stock, []).append(macds[-5] * 2)
            min_5_macd.setdefault(stock, []).append(macds[-4] * 2)
            min_5_macd.setdefault(stock, []).append(macds[-3] * 2)
            min_5_macd.setdefault(stock, []).append(macds[-2] * 2)
            min_5_macd.setdefault(stock, []).append(macds[-1] * 2)
        except:
            continue

###################################################################################

# print (min_30_macd)
# print (min_60_macd)

# Get wind stock code string
w.start()
codeList = getAllStockList()
wind_stock_codes = parseStock(codeList)
first_time = True
w.stop()
while (1):
    weekno = datetime.today().weekday()
    if weekno in [0, 1, 2, 3,4]:
        curTime = datetime.today().strftime('%H-%M')
        if curTime == '09-00':#can run at anytime 06:35
            day_signal = []

            w.start()
            today = datetime.today().strftime('%Y-%m-%d')
            dayFlag = False
            if first_time == True:
                prev_n_days = calTimeDay(today, -25)  # make sure long enough to skip holidays
                # Get previous 5 trading dates
                tradeDates = conWSDData(w.tdays(prev_n_days, today)).iloc[:, 0:1].values
                tradeDates = tradeDates[len(tradeDates) - 6:-1]  # previous 5 days
                targetDate = []
                for tDate in tradeDates:
                    cur = pd.to_datetime(str(tDate[0])).strftime('%Y-%m-%d')
                    targetDate.append(cur)
                print(targetDate)
                # Get daily MACD
                for curDate in targetDate:
                    macd_data = w.wsd(wind_stock_codes, "MACD", curDate, curDate,
                                      "MACD_L=26;MACD_S=12;MACD_N=9;MACD_IO=3;Fill=Previous;PriceAdj=F")
                    for i in range(0, len(macd_data.Codes)):
                        stock = macd_data.Codes[i]
                        stock = stock.split('.')[0]
                        macd = macd_data.Data[0][i]
                        day_macd.setdefault(stock, []).append(macd)
                        dayFlag = checkMACDSignal(day_macd[stock])
                        if dayFlag == True:
                            day_signal.append(stock)
                first_time = False
            else:
                prevTDay = str(w.tdaysoffset(-1, today, "").Times[0])
                macd_data = w.wsd(wind_stock_codes, "MACD", prevTDay, prevTDay,
                                  "MACD_L=26;MACD_S=12;MACD_N=9;MACD_IO=3;Fill=Previous;PriceAdj=F")
                print ('get current day MACD ', prevTDay)
                for i in range(0, len(macd_data.Codes)):
                    stock = macd_data.Codes[i]
                    stock = stock.split('.')[0]
                    macd = macd_data.Data[0][i]
                    day_macd.setdefault(stock, []).append(macd)
                    dayFlag = checkMACDSignal(day_macd[stock])
                    if dayFlag == True:
                        day_signal.append(stock)
                        # print(stock, ' day signal ', today)

                        # print (day_macd)
                        # print (len(day_macd.keys()))
                        # exit(0)
            w.stop()

            #Get 20day high & low and check
            histRes = []
            for root, dirs, files in os.walk(output_dir_histdata):
                for file in files:
                    stock = file.split('_')[0]
                    try:
                        data = pd.read_csv(output_dir_histdata + file, dtype=str)
                    except:
                        print(file)
                        exit(0)
                    if len(data)<20:
                        continue
                    data = data[len(data) - 20:]
                    prices_high = data['high'].values
                    price_highest = float(max(prices_high))
                    prices_low = data['low'].values
                    prices_lowest = float(min(prices_low))

                    if (price_highest - prices_lowest) / prices_lowest > 0.3:
                        histRes.append(stock)

            # print (histRes)
            day_signal_final = []
            for stock in day_signal:
                if stock in histRes:
                    day_signal_final.append(stock)
            print (today)
            print (day_signal_final)
        if '09-35' in curTime or '09-40' in curTime or '09-45' in curTime or '09-50' in curTime or '09-55' in curTime or '10-00' in curTime or '10-05' in curTime or \
                        '10-10' in curTime or '10-15' in curTime or '10-20' in curTime or '10-25' in curTime or '10-30' in curTime or '10-35' in curTime or \
                        '10-40' in curTime or '10-45' in curTime or '10-50' in curTime or '10-55' in curTime or '11-00' in curTime or '11-05' in curTime or '11-10' in curTime or \
                        '11-15' in curTime or '11-20' in curTime or '11-25' in curTime or '11-30' in curTime or '13-05' in curTime or '13-10' in curTime or '13-15' in curTime or \
                        '13-20' in curTime or '13-25' in curTime or '13-30' in curTime or '13-35' in curTime or '13-40' in curTime or '13-45' in curTime or '13-50' in curTime or \
                        '13-55' in curTime or '14-00' in curTime or '14-05' in curTime or '14-10' in curTime or '14-15' in curTime or '14-20' in curTime or '14-25' in curTime or \
                        '14-30' in curTime or '14-35' in curTime or '14-40' in curTime or '14-45' in curTime or '14-50' in curTime or '14-55' in curTime or '15-00' in curTime:
            w.start()
            print (curTime)
            min_5_flag = False
            min_30_flag = False
            min_60_flag = False
            data = w.wsq(wind_stock_codes, 'rt_last')
            for i in range(0, len(data.Codes)):
                wind_stock = data.Codes[i]
                stock = wind_stock.split('.')[0]
                rt_last = data.Data[0][i]
                datetime1 = str(data.Times[0])
                row = datetime1 + ',' + str(rt_last)

                min_5_price.setdefault(stock, []).append(rt_last)
                # save to file
                filename = output_dir_5 + stock + '_5min'
                # check file not exits
                if not Path(filename).is_file():
                    header = 'date,close'
                    fd = open(filename, 'a')
                    fd.write(header)
                    fd.write('\n')
                    fd.close()
                fd = open(filename, 'a')
                fd.write(row)
                fd.write('\n')
                fd.close()

                curMacd = talib.MACD(np.asarray(min_5_price[stock]), 12, 26, 9)[2][-1] * 2
                min_5_macd.setdefault(stock, []).append(curMacd)
                min_5_flag = checkMACDSignal(min_5_macd[stock])

                if '10-00' in curTime or '10-30' in curTime or '11-00' in curTime or '11-30' in curTime or '13-30' in curTime or '14-00' in curTime or '14-30' in curTime or '15-00' in curTime:
                    min_30_price.setdefault(stock, []).append(rt_last)
                    # save to file
                    filename = output_dir_30 + stock + '_30min'
                    #check file not exits
                    if not Path(filename).is_file():
                        header = 'date,close'
                        fd = open(filename, 'a')
                        fd.write(header)
                        fd.write('\n')
                        fd.close()
                    fd = open(filename, 'a')
                    fd.write(row)
                    fd.write('\n')
                    fd.close()

                    curMacd = talib.MACD(np.asarray(min_30_price[stock]), 12, 26, 9)[2][-1] * 2
                    min_30_macd.setdefault(stock, []).append(curMacd)
                    min_30_flag = checkMACDSignal(min_30_macd[stock])

                    # if min_30_flag == True:
                    #    print (stock, ' 30 min signal ', datetime1)

                    if '10-30' in curTime or '11-30' in curTime or '14-00' in curTime or '15-00' in curTime:
                        min_60_price.setdefault(stock, []).append(rt_last)
                        filename = output_dir_60 + stock + '_60min'
                        # check file not exits
                        if not Path(filename).is_file():
                            header = 'date,close'
                            fd = open(filename, 'a')
                            fd.write(header)
                            fd.write('\n')
                            fd.close()
                        fd = open(filename, 'a')
                        fd.write(row)
                        fd.write('\n')
                        fd.close()

                        curMacd = talib.MACD(np.asarray(min_60_price[stock]), 12, 26, 9)[2][-1] * 2
                        min_60_macd.setdefault(stock, []).append(curMacd)
                        min_60_flag = checkMACDSignal(min_60_macd[stock])
                        if min_60_flag == True:
                            if stock in day_signal_final and min_30_flag == True and min_5_flag == True:
                                    ma_data = w.wsq(wind_stock, 'rt_ma_250d')
                                    try:
                                        rt_ma_250 = ma_data.Data[0][0]
                                    except:
                                        print ('except when getting ma250')
                                        continue
                                    if rt_last > rt_ma_250:
                                        print (stock,' signal ', curTime)


            # print ('30 MIN MACD: ', min_30_macd)
            # print('60 min macd: ', min_60_macd)
            w.stop()
    sleep(55)
