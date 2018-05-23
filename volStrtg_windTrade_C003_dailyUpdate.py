# coding=utf-8
# 每日开盘前调用一次，更新config文件里的数据
from WindPy import *
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import math
import logging

logging.basicConfig(filename='windTrade_C003_dailyUpdate.log', level=logging.DEBUG)

pd.set_option('expand_frame_repr', False)


###########################Get trading date with offset####################
def getTDays(offset, passeddate):
    date_data = w.tdaysoffset(offset, passeddate, "")
    try:
        ret_date = (date_data.Data[0][0]).strftime('%Y-%m-%d')
    except:
        print('except')
        print(date_data.Data[0][0])
        print(date_data.Data[0][0].__class__.__name__)
    return ret_date


######################## Calculate date difference#########################
def calTimeDate(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')


def calTimeHour(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d %H-%M') + timedelta(hours=delta)).strftime(
        '%Y-%m-%d %H-%M')


#######################Calculate Volatility###################
def calHistoricalVolatility(prices, period):
    dailyReturn = []
    for i in range(1, period):
        dailyReturn.append(prices[i] / prices[i - 1])

    returnMean = sum(dailyReturn) / period

    diff = []
    for i in range(0, period - 1):
        diff.append(math.pow((dailyReturn[i] - returnMean), 2))

    vol = math.sqrt(sum(diff) / (period - 2)) * math.sqrt(246 / (period - 1))

    return vol


##############################Get info from stock config file######################
def getBackdays(stock):
    global stock_conf
    backdays = (stock_conf.loc[(stock_conf['Stock'] == stock)])['BackDays'].values[0]
    return int(backdays)


def getZhisunDay(stock):
    global stock_conf
    zhishun = (stock_conf.loc[(stock_conf['Stock'] == stock)])['Zhisun_day'].values[0]
    return int(zhishun)


def getZhisunPrice(stock):
    global stock_conf
    zhishunPrice = (stock_conf.loc[(stock_conf['Stock'] == stock)])['Zhisun_price'].values[0]
    return float(zhishunPrice)


def getIsFixedZhisunPrice(stock):
    global stock_conf
    IsFixZhisunPrice = (stock_conf.loc[(stock_conf['Stock'] == stock)])['IsFixZhisunPrice'].values[0]
    if IsFixZhisunPrice == 'Y':
        return True
    else:
        return False


def getStockEachTradeQuantity(stock):
    global stock_conf
    EachStockTradeQuantity = (stock_conf.loc[(stock_conf['Stock'] == stock)])['EachStockTradeQuantity'].values[0]
    return int(EachStockTradeQuantity)


def getVolAbs(stock):
    global stock_conf
    vol_abs = (stock_conf.loc[(stock_conf['Stock'] == stock)])['VolAbs'].values[0]
    return float(vol_abs)


def getLastTradeType(stock):
    global stock_conf
    last_trade_type = (stock_conf.loc[(stock_conf['Stock'] == stock)])['LastTradeType'].values[0]
    return str(last_trade_type)


def getUpRangeOpenFlag(stock):
    global stock_conf
    up_open_flag = (stock_conf.loc[(stock_conf['Stock'] == stock)])['UpOpenFlag'].values[0]
    return str(up_open_flag)


def getDownRangeOpenFlag(stock):
    global stock_conf
    down_open_flag = (stock_conf.loc[(stock_conf['Stock'] == stock)])['DownOpenFlag'].values[0]
    return str(down_open_flag)


def getExecTFlag(stock):
    global stock_conf
    exec_t_flag = (stock_conf.loc[(stock_conf['Stock'] == stock)])['ExecTFlag'].values[0]
    return str(exec_t_flag)


def getBuyLeft(stock):
    global stock_conf
    buy_left = (stock_conf.loc[(stock_conf['Stock'] == stock)])['BuyLeft'].values[0]
    return int(buy_left)


def getSellLeft(stock):
    global stock_conf
    sell_left = (stock_conf.loc[(stock_conf['Stock'] == stock)])['SellLeft'].values[0]
    return int(sell_left)


def getVolUp1(stock):
    global stock_conf
    vol_up_1 = (stock_conf.loc[(stock_conf['Stock'] == stock)])['VolUp1'].values[0]
    return float(vol_up_1)


def getVolUp2(stock):
    global stock_conf
    vol_up_2 = (stock_conf.loc[(stock_conf['Stock'] == stock)])['VolUp2'].values[0]
    return float(vol_up_2)


def getVolUp3(stock):
    global stock_conf
    vol_up_3 = (stock_conf.loc[(stock_conf['Stock'] == stock)])['VolUp3'].values[0]
    return float(vol_up_3)


def getVolDown4(stock):
    global stock_conf
    vol_down_4 = (stock_conf.loc[(stock_conf['Stock'] == stock)])['VolDown4'].values[0]
    return float(vol_down_4)


def getVolDown5(stock):
    global stock_conf
    vol_down_5 = (stock_conf.loc[(stock_conf['Stock'] == stock)])['VolDown5'].values[0]
    return float(vol_down_5)


def getVolDown6(stock):
    global stock_conf
    vol_down_6 = (stock_conf.loc[(stock_conf['Stock'] == stock)])['VolDown6'].values[0]
    return float(vol_down_6)


def getSpecialZhisunFlag(stock):
    global stock_conf
    special_zhisun_flag = (stock_conf.loc[(stock_conf['Stock'] == stock)])['SpecialZhisunFlag'].values[0]
    return str(special_zhisun_flag)


def getSpecialZhisunPrice(stock):
    global stock_conf
    spe_zhisun_price = (stock_conf.loc[(stock_conf['Stock'] == stock)])['SpecialZhisunPrice'].values[0]
    return float(spe_zhisun_price)


def getSpecialZhisunDay(stock):
    global stock_conf
    spe_zhisun_day = (stock_conf.loc[(stock_conf['Stock'] == stock)])['SpecialZhisunDay'].values[0]
    return int(spe_zhisun_day)


def getOpenTradeType(stock):
    global stock_conf
    open_trade_type = (stock_conf.loc[(stock_conf['Stock'] == stock)])['OpenTradeType'].values[0]
    return str(open_trade_type)


def getOpenTradeQuantity(stock):
    global stock_conf
    open_trade_quantity = (stock_conf.loc[(stock_conf['Stock'] == stock)])['OpenTradeQuantity'].values[0]
    return int(open_trade_quantity)


def getOpenTradeId(stock):
    global stock_conf
    open_trade_id = (stock_conf.loc[(stock_conf['Stock'] == stock)])['OpenTradeId'].values[0]
    return str(open_trade_id)


def getFirstTimeBuyFactor(stock):
    global stock_conf
    first_time_buy_factor = (stock_conf.loc[(stock_conf['Stock'] == stock)])['FirstTimeBuyFactor'].values[0]
    return float(first_time_buy_factor)


###############################Update config info dataframe#####################
def updateConfig(stock, fields, values):
    global stock_conf
    stock_conf.at[stock_conf['Stock'] == stock, fields] = values


##############################convert WIND data to DF###########################
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


##########################Update Special Zhisun data############################
def updateSpecialZhisunData(prev_t_day):
    global stock_conf
    stocks = list(stock_conf['Stock'].values)
    for stock in stocks:
        special_zhisun_flag = getSpecialZhisunFlag(stock)
        if special_zhisun_flag == 'Y':
            special_zhisun_day = getSpecialZhisunDay(stock)
            special_zhisun_price = float(w.wsd(stock, "MA", prev_t_day, prev_t_day,
                                               "MA_N=" + str(special_zhisun_day) + ";Fill=Previous;PriceAdj=F").Data[
                                             0][-1])
            updateConfig(stock, ["SpecialZhisunPrice"], [special_zhisun_price])
        else:
            prev_10_day = getTDays(-10, prev_t_day)
            price_low_11_day = \
                w.wsd(stock, "low", prev_10_day, prev_t_day, "Fill=Previous;PriceAdj=F").Data[0]
            price_lowest_10 = min(price_low_11_day[0:10])  # not including prev_t_day
            last_close = float(
                w.wsd(stock, "close", prev_t_day, prev_t_day, "Fill=Previous;PriceAdj=F").Data[0][
                    -1])  # yesterday close
            if (last_close - price_lowest_10) / price_lowest_10 > 0.3:
                five_flag = False
                ten_flag = False
                twenty_flag = False
                price_close_11_day = \
                    w.wsd(stock, "close", prev_10_day, prev_t_day, "Fill=Previous;PriceAdj=F").Data[0]
                price_close_10_day = price_close_11_day[0:10]
                five_avg_11_day = \
                    w.wsd(stock, "MA", prev_10_day, prev_t_day, "MA_N=5;Fill=Previous;PriceAdj=F").Data[0]
                five_avg_10_day = five_avg_11_day[0:10]
                for i in range(len(price_close_10_day)):
                    if price_close_10_day[i] < five_avg_10_day[i]:
                        five_flag = True
                if five_flag == True:
                    ten_avg_11_day = \
                        w.wsd(stock, "MA", prev_10_day, prev_t_day,
                              "MA_N=10;Fill=Previous;PriceAdj=F").Data[0]
                    ten_avg_10_day = ten_avg_11_day[0:10]
                    for i in range(len(price_close_10_day)):
                        if price_close_10_day[i] < ten_avg_10_day[i]:
                            ten_flag = True
                    if ten_flag == True:
                        twenty_avg_11_day = w.wsd(stock, "MA", prev_10_day, prev_t_day,
                                                  "MA_N=20;Fill=Previous;PriceAdj=F").Data[0]
                        twenty_avg_10_day = twenty_avg_11_day[0:10]
                        for i in range(len(price_close_10_day)):
                            if price_close_10_day[i] < twenty_avg_10_day[i]:
                                twenty_flag = True
                        if twenty_flag == False:  ########Within 10 days, close has not been lower than 20 days average##############
                            special_zhisun_day[stock] = 20
                            special_zhisun_price[stock] = twenty_avg_11_day[-1]
                    else:  ########Within 10 days, close has not been lower than 10 days average##############
                        special_zhisun_day = 10
                        special_zhisun_price = ten_avg_11_day[-1]
                else:  ########Within 10 days, close has not been lower than 5 days average##############
                    special_zhisun_day = 5
                    special_zhisun_price = five_avg_11_day[-1]
                updateConfig(stock, ['SpecialZhisunFlag', 'SpecialZhisunPrice', 'SpecialZhisunDay'],
                             ['Y', special_zhisun_price, special_zhisun_day])


##############################Update daily Vol numbers########################
def updateDailyVols(prev_t_day):
    global stock_conf
    stocks = list(stock_conf['Stock'].values)
    for stock in stocks:
        backDays = getBackdays(stock)
        prev_backDays_tday = getTDays(-backDays + 1, prev_t_day)
        price_close_vol = \
            w.wsd(stock, "close", prev_backDays_tday, prev_t_day, "Fill=Previous;PriceAdj=F").Data[0]

        vol_abs = float(abs(calHistoricalVolatility(price_close_vol, len(price_close_vol))))
        volUp2 = float(price_close_vol[-1] + vol_abs)
        volDown5 = float(price_close_vol[-1] - vol_abs)

        updateConfig(stock, ['VolAbs', 'VolUp2', 'VolDown5'],
                     [vol_abs, volUp2, volDown5])


#####################Update daily start position###################
def updateDailyStartPosition():
    w.tlogon("0000", "0", "W124041900431", "********", "SHSZ")
    daily_start_position = conWSQData(w.tquery('Position', 'LogonID=1'))
    w.tlogout(LogonID=1)

    if 'SecurityCode' not in daily_start_position.columns:
        return
    stocks = list(daily_start_position['SecurityCode'].values)
    for stock in stocks:
        position = int(
            (daily_start_position.loc[(daily_start_position['SecurityCode'] == stock)])['SecurityVolume'].values[0])
        updateConfig(stock, ['DailyStartPosition'],
                     [position])


#####################Update daily MA zhisun price###################
def updateDailyZhisunPrice(prev_t_day):
    global stock_conf
    stocks = list(stock_conf['Stock'].values)
    for stock in stocks:
        isFixZhisun = getIsFixedZhisunPrice(stock)
        if isFixZhisun == False:
            zhisun_day = getZhisunDay(stock)
            zhisun_p = float(w.wsd(stock, "MA", prev_t_day, prev_t_day,
                                   "MA_N=" + str(zhisun_day) + ";Fill=Previous;PriceAdj=F").Data[0][-1])
            updateConfig(stock, ['Zhisun_price'],
                         [zhisun_p])


def updateOtherVariable():##should add execTFlag to 'Y'
    global stock_conf
    stocks = list(stock_conf['Stock'].values)
    for stock in stocks:
        updateConfig(stock, ['LastTradeType', "UpOpenFlag", "DownOpenFlag", "BuyLeft", "SellLeft", "VolUp1", "VolUp3",
                             "VolDown4", "VolDown6", "OpenTradeType", "OpenTradeQuantity","OpenTradePrice", "OpenTradeId", "ExecTFlag"],
                     ["NV", "Close", "Close", 4, 4, 0.0, 0.0, 0.0, 0.0, "NV", 0, 0.0, "0", "Y"])


###############################Load config info from file#####################
def loadConfig():
    global stock_conf
    stock_conf = pd.read_csv(stock_config_file, dtype=str)


#####################initialize variables############################
data_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/"
stock_config_file = data_dir + 'stock_conf_wind_test_C003_v2.csv'
stock_conf = pd.DataFrame


#########################################Start##########################################################################
def main():
    w.start()
    today = datetime.today().strftime('%Y-%m-%d')
    prev_t_day = getTDays(-1,
                          today)  # if today is weekend, then previous 1 trading day would be Thursday, treat weekends as Friday
    print('prev t day ' + prev_t_day)
    loadConfig()
    print('loaded original config file')
    updateDailyVols(prev_t_day)
    print('updated daily vol data')
    updateSpecialZhisunData(prev_t_day)
    print('updated daily special zhisun data')
    updateDailyZhisunPrice(prev_t_day)
    print('updated daily zhisun data')
    updateDailyStartPosition()
    print('updated daily start stock position')
    updateOtherVariable()
    print ('reset other variables')
    print(stock_conf)
    stock_conf.to_csv(stock_config_file, index=False)
    print('write change to file')
    w.stop()
    print('done')


if __name__ == '__main__':
    main()