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

w.start()

#1. Get minute data from Wind before trading day starts, and save them to file, 1 stock per file with only price
#2. Get real time minute data, and save them to file


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


def checkMACDSignal(macds):
    if len(macds) < 5:
        return False
    # print (macds)
    flag = False
    if macds[-5] < 0 and macds[-4] < 0 and macds[-3] < 0 and macds[-2] < 0 and macds[-1] < 0 and \
                    macds[-5] > macds[-4] and macds[-4] > macds[-3] and macds[-3] > macds[
        -2] and macds[-2] < macds[-1]:
        flag = True
    return flag


########################################################################################################
day_price = []
min_30_price = {}
min_60_price = {}

min_30_macd = {}
min_60_macd = {}

day_macd = {}
#
data_dir = "C:/KeLiQuant/"
today = datetime.today().strftime('%Y-%m-%d')
today = '2018-04-18'#This is CN today, US next day
prev_n_days = calTimeDay(today, -25)  # make sure long enough to skip holidays

stock_codes = pd.read_csv(data_dir + 'codeList.txt', dtype=str)['stock'].values
# Get history minute prices
ct = 0
for stock in stock_codes:
        # ct = ct +1
        # if ct<=1000:
            print (stock)
            try:
                price_data_df = ts.get_hist_data(stock, start=prev_n_days, end=today, ktype='30', retry_count=10,
                                                 pause=3)  # not including today's data
            except:
                print(stock, ' has not got data')
                continue
            if price_data_df is None:
                continue
            price_data_df.sort_index(inplace=True)
            min_30_price[stock] = list(price_data_df['close'].values)
            try:
                price_data_df = ts.get_hist_data(stock, start=prev_n_days, end=today, ktype='60', retry_count=10,
                                                 pause=3)  # not including today's data
            except:
                print(stock, ' has not got data')
            if price_data_df is None:
                continue
            price_data_df.sort_index(inplace=True)
            min_60_price[stock] = list(price_data_df['close'].values)

print(str(len(min_30_price)), ' stock have 30/60 min data from tushare')

# Get wind stock code string
w.start()
codeList = getAllStockList()
wind_stock_codes = parseStock(codeList)
first_time = True

while (1):
    weekno = datetime.today().weekday()
    if weekno in [0, 1, 2, 3,6]:
        curTime = datetime.today().strftime('%H-%M')
        if (curTime == '18-00'):  # should be 10:00
            w.start()
            today = datetime.today().strftime('%Y-%m-%d')#This is US today, CN tomorrow
            dayFlag = False
            if first_time == True:
                prev_n_days = calTimeDay(today, -25)  # make sure long enough to skip holidays
                # Get previous 5 trading dates
                tradeDates = conWSDData(w.tdays(prev_n_days, today)).iloc[:, 0:1].values
                tradeDates = tradeDates[len(tradeDates) - 5:]  # previous 5 days
                targetDate = []
                for tradeDate in tradeDates:
                    cur = pd.to_datetime(str(tradeDate[0])).strftime('%Y-%m-%d')
                    targetDate.append(cur)
                print(targetDate)
                # exit(0)
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
                            print(stock, ' day signal ', today)
                first_time = False
            else:
                macd_data = w.wsd(wind_stock_codes, "MACD", today, today,
                                  "MACD_L=26;MACD_S=12;MACD_N=9;MACD_IO=3;Fill=Previous;PriceAdj=F")
                for i in range(0, len(macd_data.Codes)):
                    stock = macd_data.Codes[i]
                    stock = stock.split('.')[0]
                    macd = macd_data.Data[0][i]
                    day_macd.setdefault(stock, []).append(macd)
                    dayFlag = checkMACDSignal(day_macd[stock])
                    if dayFlag == True:
                        print(stock, ' day signal ', today)

                        # print (day_macd)
                        # print (len(day_macd.keys()))
                        # exit(0)

        dateTime = datetime.today().strftime('%Y-%m-%d %H-%M')
        dateTime = calTimeHour(dateTime, +15)
        # print (dateTime)
        curTime = dateTime.split(' ')[1]
        # print ("current time: ", str(curTime))
        if '10-00' in curTime or '10-30' in curTime or '11-00' in curTime or '11-30' in curTime or '13-30' in curTime or '14-00' in curTime or '14-30' in curTime or '15-00' in curTime:

            print (curTime)
            if '10-00' in curTime:
                w.start()
            min_30_flag = False
            min_60_flag = False
            data = w.wsq(wind_stock_codes, 'rt_last')
            print (data)
            for i in range(0, len(data.Codes)):
                stock = data.Codes[i]
                stock = stock.split('.')[0]

                # if stock not in min_30_price.keys():
                #     continue
                print(stock)
                rt_last = data.Data[0][i]
                min_30_price.setdefault(stock, []).append(rt_last)
                # print (min_30_price)
                curMacd = talib.MACD(np.asarray(min_30_price[stock]), 12, 26, 9)[2][-1] * 2
                print (curMacd)
                min_30_macd.setdefault(stock, []).append(curMacd)
                min_30_flag = checkMACDSignal(min_30_macd[stock])
                if min_30_flag == True:
                    print(stock, ' 30 min signal ', dateTime)
                if '10-30' in dateTime or '11-30' in dateTime or '14-00' in dateTime or '15-00' in dateTime:
                    if stock not in min_60_price.keys():
                        continue
                    min_60_price.setdefault(stock, []).append(rt_last)
                    curMacd = talib.MACD(np.asarray(min_60_price[stock]), 12, 26, 9)[2][-1] * 2
                    min_60_macd.setdefault(stock, []).append(curMacd)
                    min_60_flag = checkMACDSignal(min_60_macd[stock])
                    if min_60_flag == True:
                        print(stock, ' 60 min signal ', dateTime)

            # for stock in min_30_macd.keys():
            #     print (stock)
            #     print (min_30_macd[stock])
            # print ('30 min price: ',min_30_price)
            # print('60 min price: ', min_60_price)
            print ('30 MIN MACD: ', min_30_macd)
            print('60 min macd: ', min_60_macd)
    sleep(57)
