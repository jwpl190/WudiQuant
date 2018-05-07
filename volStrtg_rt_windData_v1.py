# coding=utf-8
from WindPy import *
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import math
import pickle
pd.set_option('expand_frame_repr', False)

###########################round to 100################
def truncate(f, n):
    '''Truncates/pads a int f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])
############################upper interval has been opened, update all intervals############################
def updateRangesFromUp(vol_abs, price, stock, stock_vol_range_all, stock_vol_range_up, stock_vol_range_down):
    volUp1 = price + vol_abs * 0.5
    volUp2 = price
    volUp3 = price - vol_abs * 0.5

    volDown4 = price - vol_abs * 1.5
    volDown5 = price - vol_abs * 2
    volDown6 = price - vol_abs * 2.5

    # (aaa,bbb]
    all_range_vol = [(sys.float_info.max, volUp1), (volUp1, volUp2), (volUp2, volUp3), (volUp3, volDown4),
                     (volDown4, volDown5), (volDown5, volDown6), (volDown6, sys.float_info.min)]

    up_range_vol = [(sys.float_info.max, volUp1), (volUp1, volUp2), (volUp2, volUp3), (volUp3, volDown5),
                    (volDown5, sys.float_info.min)]

    down_range_vol = [(sys.float_info.max, volUp2), (volUp2, volDown4), (volDown4, volDown5), (volDown5, volDown6),
                      (volDown6, sys.float_info.min)]

    stock_vol_range_all[stock] = all_range_vol
    stock_vol_range_up[stock] = up_range_vol
    stock_vol_range_down[stock] = down_range_vol


############################lower interval has been opened, update all intervals############################

def updateRangesFromDown(vol_abs, price, stock, stock_vol_range_all, stock_vol_range_up, stock_vol_range_down):
    volUp1 = price + vol_abs * 2.5
    volUp2 = price + vol_abs * 2
    volUp3 = price + vol_abs * 1.5

    volDown4 = price + vol_abs * 0.5
    volDown5 = price
    volDown6 = price - vol_abs * 0.5

    # (aaa,bbb]
    all_range_vol = [(sys.float_info.max, volUp1), (volUp1, volUp2), (volUp2, volUp3), (volUp3, volDown4),
                     (volDown4, volDown5), (volDown5, volDown6), (volDown6, sys.float_info.min)]

    up_range_vol = [(sys.float_info.max, volUp1), (volUp1, volUp2), (volUp2, volUp3), (volUp3, volDown5),
                    (volDown5, sys.float_info.min)]

    down_range_vol = [(sys.float_info.max, volUp2), (volUp2, volDown4), (volDown4, volDown5), (volDown5, volDown6),
                      (volDown6, sys.float_info.min)]

    stock_vol_range_all[stock] = all_range_vol
    stock_vol_range_up[stock] = up_range_vol
    stock_vol_range_down[stock] = down_range_vol


###########################Get trading date with offset####################
def getTDays(offset, date):
    date_data = w.tdaysoffset(offset, date, "")
    date = date_data.Data[0][0]
    return date.strftime('%Y-%m-%d')


###########################Parse stock list for Wind query#####################
def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes


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


#############################delete zhisun stocks, if need to reuse them, set BackFalg to Y and make it first time################################
# def getAllStocks(stock_conf):
#     orig_stocks = stock_conf['Stock'].values
#     ret_stock = []
#     for stock in orig_stocks:
#         if stock in zhisun_stock:
#             backFlag = (stock_conf.loc[(stock_conf['Stock'] == stock)])['BackFlag'].values[0]
#             if backFlag == 'Y':
#                 ret_stock.append(stock)
#                 first_time[stock] = True
#         else:
#             ret_stock.append(stock)
#     for stock in ret_stock:
#         if stock in zhisun_stock:
#             zhisun_stock.remove(stock)
#         if stock in zhisun_stock_temp:
#             zhisun_stock_temp.remove(stock)
#     return ret_stock


###########################update stocks list after zhisun happend and stock quantity is 0 #########################
# def updateAllStocks():
#     for stock in zhisun_stock:
#         if stock in stocks:
#             stocks.remove(stock)
#             backFlag = (stock_conf.loc[(stock_conf['Stock'] == stock)])['BackFlag'].values[0]
#             if backFlag == 'Y':
#                 updateConfig(stock, ["BackFlag"], ['N'])
#     return stocks


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


def getStockPosition(stock):
    global stock_conf
    position = (stock_conf.loc[(stock_conf['Stock'] == stock)])['Position'].values[0]
    return int(position)


def getStockEachTradeQuantity(stock):
    global stock_conf
    EachStockTradeQuantity = (stock_conf.loc[(stock_conf['Stock'] == stock)])['EachStockTradeQuantity'].values[0]
    return int(EachStockTradeQuantity)


def getStockDailySellable(stock):
    global stock_conf
    StockDailySellable = (stock_conf.loc[(stock_conf['Stock'] == stock)])['StockDailySellable'].values[0]
    return int(StockDailySellable)


def getIsManualAdd(stock):
    global stock_conf
    IsManualAdd = (stock_conf.loc[(stock_conf['Stock'] == stock)])['IsManualAdd'].values[0]
    if IsManualAdd == 'Y':
        return True
    else:
        return False


def getIsFixedZhisunPrice(stock):
    global stock_conf
    IsFixZhisunPrice = (stock_conf.loc[(stock_conf['Stock'] == stock)])['IsFixZhisunPrice'].values[0]
    if IsFixZhisunPrice == 'Y':
        return True
    else:
        return False


##############################check weimai weimai######################
def checkWeimai(stock):
    wdata = w.wsq(stock, 'rt_bsize_total,rt_asize_total')
    bsize_total = wdata.Data[0][0]
    asize_total = wdata.Data[1][0]
    if asize_total == 0 or bsize_total == 0:
        return False
    if asize_total / bsize_total >= 3 or bsize_total / asize_total >= 3:
        return True
    else:
        return False


##############################sell function######################
def sellFunc(stock, last, sellType, buy_left, sell_left, vol_last_trade_type,position):
    if sell_left[stock] > 0:
        global stock_conf
        each_stock_trade_quantity = getStockEachTradeQuantity(stock)
        sellable_quantity =  getStockDailySellable(stock)
        trade_quantity = min(sellable_quantity, each_stock_trade_quantity)
        trade_quantity =int(float(truncate(trade_quantity / 100, 0)) * 100)
        print("should sell ", str(trade_quantity), ', sell type: ', sellType)
        vol_last_trade_type[stock] = sellType
        trade_price = last * 0.998

        ######Trade API
        # order_shares(stock, trade_sell * (-1), style=LimitOrder(trade_price))
        # trade_quantity = someAPI
        #########
        sell_left[stock] = sell_left[stock] - 1
        buy_left[stock] = buy_left[stock] + 1

        updateConfig(stock, ["Position","StockDailySellable"], [position - trade_quantity,sellable_quantity-trade_quantity])

    else:
        print("no more sell left")


##############################buy function######################
def buyFunc(stock, last, buyType, isDouble, buy_left, vol_last_trade_type,position):
    if buy_left[stock] > 0:
        global stock_conf
        each_stock_trade_quantity = getStockEachTradeQuantity(stock)
        if isDouble == True:
            trade_quantity = each_stock_trade_quantity * 2
        else:
            trade_quantity = each_stock_trade_quantity
        trade_quantity = int(float(truncate(trade_quantity / 100, 0)) * 100)
        print(buyType)
        vol_last_trade_type[stock] = buyType
        trade_price = last * 1.002
        #####Trade type###
        # order_shares(stock, trade_quantity, style=LimitOrder(trade_price))
        # trade_quantity = someAPI
        
        updateConfig(stock, ["Position"], [position + trade_quantity])
        buy_left[stock] = buy_left[stock] - 1
    else:
        print("no more buy left")

##############################buy first trade function######################
def buyFirstFunc(stock, last):
    global each_stock_cash
    buy_cash = each_stock_cash[stock] / 2  # use half of the cash to buy
    trade_price = last * 1.002
    trade_quantity = buy_cash / trade_price
    if trade_quantity < 400:
        trade_quantity = 400
        buy_cash = trade_quantity * trade_price
    trade_quantity = int(float(truncate(trade_quantity / 100, 0)) * 100)

    each_trade_quantity = trade_quantity / 4
    each_trade_quantity = int(float(truncate(each_trade_quantity / 100, 0)) * 100)
    ###trade api####
    # order_value(stock, buy_cash, style=LimitOrder(trade_price))
    # trade_quantity = someAPI

    ####trade api###
    updateConfig(stock, ["Position", "EachStockTradeQuantity"], [
        trade_quantity, each_trade_quantity])  # postion & volatility strategy trade volume

###############################Load config info from file#####################
def loadConfig():
    global stock_conf
    stock_conf = pd.read_csv(stock_config_file, dtype=str)
    ####### get all stocks####################
    stocks = list(stock_conf['Stock'].values)
    number_of_stocks = len(stocks)
    for stock in stocks:
        if stock not in each_stock_cash:
            each_stock_cash[stock] = cash / number_of_stocks
        if stock not in first_time:
            isManualAdd = getIsManualAdd(stock)
            if isManualAdd == True:  # no need to buy first time
                first_time[stock] = False
            else:
                first_time[stock] = True


###############################Update config info dataframe#####################
def updateConfig(stock, fields, values):
    global stock_conf
    stock_conf.at[stock_conf['Stock'] == stock, fields] = values


#####################initialize variables############################
data_dir = "C:\KeLiQuant\\"
stock_config_file = data_dir + 'stock_conf_wind.txt'
zhisun_stock_temp = []
special_zhisun_price = {}
special_zhisun_day = {}
cash = 1000000
each_stock_cash = {}
number_of_stocks = 10
first_time = {}
stock_conf = pd.DataFrame

REGISTRY = None


#########################################Start##########################################################################
def main(start=0):
    a = start
    global REGISTRY
    while 1:
        weekno = datetime.today().weekday()
        if weekno in [0, 1, 2, 3, 4]:  # should be [0,1,2,3,4]

            # stocks = ["002049.SZ"]  #################need to delete@#################################################################
            date_time = datetime.today().strftime('%Y-%m-%d %H-%M')
            today = date_time.split(' ')[0]
            ###########################
            curTime = date_time.split(' ')[1]
            ####################################before trading daily#############################################################
            if curTime == '12-43':
                w.start()
                loadConfig()
                prev_t_day = getTDays(-1,
                                      today)  # if today is weekend, then previous 1 trading day would be Thursday, treat weekends as Friday

                print("today is : ", today)
                print("previous trading day is : ", prev_t_day)
                ####### reset daily use variables#######
                stock_vol_range_all = {}
                stock_vol_range_up = {}
                stock_vol_range_down = {}
                stock_vol = {}
                stock_vol_abs = {}
                stock_exec_flag = {}
                vol_up_open_flag = {}
                vol_down_open_flag = {}
                vol_last_trade_type = {}
                sell_left = {}
                buy_left = {}
                price_highest_20 = {}
                year_avg = {}
                thirty_avg = {}
                global stock_conf
                stocks = list(stock_conf['Stock'].values)

                for stock in stocks:
                    print(stock)
                    #############no position, if not first time, need to buy using jun xian strategy##########################
                    position = getStockPosition(stock)
                    if position == 0:
                        year_avg[stock] = \
                            w.wsd(stock, "MA", prev_t_day, prev_t_day, "MA_N=255;Fill=Previous;PriceAdj=F").Data[0][-1]
                        thirty_avg[stock] = \
                            w.wsd(stock, "MA", prev_t_day, prev_t_day, "MA_N=30;Fill=Previous;PriceAdj=F").Data[0][-1]
                        prev_19_day = getTDays(-19, prev_t_day)
                        price_highest_20[stock] = max(
                            w.wsd(stock, "high", prev_19_day, prev_t_day, "Fill=Previous;PriceAdj=F").Data[0])
                    ###################Special zhi sun strategy##########################
                    if stock in special_zhisun_day.keys():
                        teshu_zhisun_day = str(special_zhisun_day[stock])
                        special_zhisun_price[stock] = float(w.wsd(stock, "MA", prev_t_day, prev_t_day,
                                                            "MA_N=" + teshu_zhisun_day + ";Fill=Previous;PriceAdj=F").Data[
                            0][-1])
                    else:
                        prev_10_day = getTDays(-10, prev_t_day)
                        price_low_11_day = w.wsd(stock, "low", prev_10_day, prev_t_day, "Fill=Previous;PriceAdj=F").Data[0]
                        price_lowest_10 = min(price_low_11_day[0:10])  # not including prev_t_day
                        last_close = float(w.wsd(stock, "close", prev_t_day, prev_t_day, "Fill=Previous;PriceAdj=F").Data[0][
                            -1] ) # yesterday close
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
                                    special_zhisun_day[stock] = 10
                                    special_zhisun_price[stock] = ten_avg_11_day[-1]
                            else:  ########Within 10 days, close has not been lower than 5 days average##############
                                special_zhisun_day[stock] = 5
                                special_zhisun_price[stock] = five_avg_11_day[-1]
                    ########Calculate volatility######################
                    backDays = getBackdays(stock)
                    prev_backDays_tday = getTDays(-backDays + 1, prev_t_day)
                    price_close_vol = \
                        w.wsd(stock, "close", prev_backDays_tday, prev_t_day, "Fill=Previous;PriceAdj=F").Data[0]

                    vol_abs = abs(calHistoricalVolatility(price_close_vol, len(price_close_vol)))
                    volUp1 = price_close_vol[-1] + vol_abs * 1.5
                    volUp2 = price_close_vol[-1] + vol_abs
                    volUp3 = price_close_vol[-1] + vol_abs * 0.5

                    volDown4 = price_close_vol[-1] - vol_abs * 0.5
                    volDown5 = price_close_vol[-1] - vol_abs
                    volDown6 = price_close_vol[-1] - vol_abs * 1.5

                    # (aaa,bbb]#########Initial 3 ranges (may not be needed)#############
                    all_range_vol = [(sys.float_info.max, volUp1), (volUp1, volUp2), (volUp2, volUp3),
                                     (volUp3, volDown4),
                                     (volDown4, volDown5), (volDown5, volDown6), (volDown6, sys.float_info.min)]

                    up_range_vol = [(sys.float_info.max, volUp1), (volUp1, volUp2), (volUp2, volUp3),
                                    (volUp3, volDown5),
                                    (volDown5, sys.float_info.min)]

                    down_range_vol = [(sys.float_info.max, volUp2), (volUp2, volDown4), (volDown4, volDown5),
                                      (volDown5, volDown6), (volDown6, sys.float_info.min)]

                    stock_vol_range_all[stock] = all_range_vol
                    stock_vol_range_up[stock] = up_range_vol
                    stock_vol_range_down[stock] = down_range_vol
                    stock_vol.setdefault(stock, [])
                    stock_vol[stock].append(volUp2)  ####initial 2nd line######
                    stock_vol[stock].append(volDown5)  #####initial 5th line######
                    stock_vol_abs[stock] = vol_abs

                    #############################
                    stock_exec_flag[
                        stock] = True  ## After buying for the first time, do volatility trading from next day######
                    vol_up_open_flag[stock] = False  # 2nd line
                    vol_down_open_flag[stock] = False  # 5th line
                    vol_last_trade_type[stock] = ''  # last time trading type
                    sell_left[stock] = 4  # max number of selling
                    buy_left[stock] = 4  # max number of buying
                    updateConfig(stock, ["StockDailySellable"],[position])# each day sellable quantity for each stock

                    sleep(1)
                w.stop()
                print ("DONE daily before trading process")
            ###########################################################trading#####################################################################
            elif (curTime >= '09-30' and curTime <= '11-30') or (curTime >= '13-00' and curTime <= '15-00'):
                w.start()
                print('START this minute')
                # load config file every minute
                loadConfig()

                stocks = list(stock_conf['Stock'].values)
                for stock in stocks:
                    wdata = w.wsq(stock, 'rt_last')
                    last = float(wdata.Data[0][0])
                    position = getStockPosition(stock)
                    if position == 0:
                        # if zhisun happened, abandon this stock
                        if stock in zhisun_stock_temp:

                            stock_conf = stock_conf[stock_conf.Stock != stock]
                            zhisun_stock_temp.remove(stock)
                            continue
                        # first time, force to buy
                        if first_time[stock] == True:
                            print(stock, ' buy first time')
                            buyFirstFunc(stock,last)
                            stock_exec_flag[stock] = False  # start volatility trade next day
                            first_time[stock] = False
                        # jun xian strategy reenter to market, not first time
                        else:
                            if last >= price_highest_20[stock]:
                                if last >= year_avg[stock] and thirty_avg[stock] >= year_avg[stock]:
                                    print(stock, ' jun xian buy signal')
                                    buyFirstFunc(stock,last)
                                    stock_exec_flag[stock] = False
                    else:
                        # special zhisun
                        if stock in special_zhisun_price.keys():
                            if last <= special_zhisun_price[stock]:
                                if stock not in zhisun_stock_temp:
                                    zhisun_stock_temp.append(stock)
                                print("sell - special zhi sun ", stock)

                        # Get zhisun (zhisun_day or zhisun_price)
                        isFixZhisun = getIsFixedZhisunPrice(stock)
                        if isFixZhisun == True:
                            zhisun_p = getZhisunPrice(stock)
                        else:
                            prev_t_day = getTDays(-1, today)
                            zhisun_day = getZhisunDay(stock)
                            zhisun_p = float(w.wsd(stock, "MA", prev_t_day, prev_t_day,
                                             "MA_N=" + str(zhisun_day) + ";Fill=Previous;PriceAdj=F").Data[0][-1])
                        # fixed price zhisun
                        if last <= zhisun_p or stock in zhisun_stock_temp:
                            print("sell - zhi sun ", stock)
                            sellable_quantity = getStockDailySellable(stock)
                            trade_price = last * 0.998
                            ###trade api####
                            # order_shares(stock, sellable_quantity * (-1), style=LimitOrder(trade_price))
                            # trade_quantity = someAPI
                            trade_quantity = sellable_quantity

                            # trade_quantity = int(truncate(trade_quantity / 100, 0)) * 100
                            ####trade api###
                            updateConfig(stock, ["Position", "StockDailySellable"],[position - trade_quantity, sellable_quantity - trade_quantity])
                            if stock not in zhisun_stock_temp:
                                zhisun_stock_temp.append(stock)
                            continue
                        # volatility strategy
                        if stock_exec_flag[stock] == True:
                            # all intervals open
                            if vol_up_open_flag[stock] == True and vol_down_open_flag[stock] == True:
                                for r in stock_vol_range_all[stock]:
                                    if r[0] > last and last >= r[1]:
                                        range_index = stock_vol_range_all[stock].index(r)
                                        break
                                # price is at 1st interval
                                if range_index == 0:
                                    # last trade was sell2, buy2, sell3,buy3,sell4,buy4,sell5,buy5,buy6  --> sell1
                                    if vol_last_trade_type[stock] == 'sell2' or vol_last_trade_type[stock] == 'buy2' or \
                                                    vol_last_trade_type[
                                                        stock] == 'sell3' or vol_last_trade_type[stock] == 'buy3' or \
                                                    vol_last_trade_type[stock] == 'sell4' or vol_last_trade_type[
                                        stock] == 'buy4' or vol_last_trade_type[stock] == 'sell5' or \
                                                    vol_last_trade_type[stock] == 'buy5' or vol_last_trade_type[
                                        stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'a')
                                            sellFunc(stock, last, 'sell1', buy_left, sell_left, vol_last_trade_type,position)
                                # price is at 2nd interval
                                elif range_index == 1:
                                    # last trade was sell3,buy3,sell4,buy4,sell5,buy5,buy6  --> sell2
                                    if vol_last_trade_type[stock] == 'sell3' or vol_last_trade_type[
                                        stock] == 'buy3' or vol_last_trade_type[stock] == 'sell4' or \
                                                    vol_last_trade_type[stock] == 'buy4' or vol_last_trade_type[
                                        stock] == 'sell5' or vol_last_trade_type[stock] == 'buy5' or \
                                                    vol_last_trade_type[stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'b')
                                            sellFunc(stock, last, 'sell2', buy_left, sell_left, vol_last_trade_type,position)
                                # price is at 3rd interval
                                elif range_index == 2:
                                    # last trade was sell1  --> buy2
                                    if vol_last_trade_type[stock] == 'sell1':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'c')
                                            buyFunc(stock, last, 'buy2', False, buy_left, vol_last_trade_type,position)
                                    # last trade was buy5,buy6  --> sell3
                                    elif vol_last_trade_type[stock] == 'buy5' or vol_last_trade_type[stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'd')
                                            sellFunc(stock, last, 'sell3', buy_left, sell_left, vol_last_trade_type,position)
                                # price is at 4th interval
                                elif range_index == 3:
                                    # last trade was sell1，sell2 --> buy3
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[stock] == 'sell2':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'e')
                                            buyFunc(stock, last, 'buy3', False, buy_left, vol_last_trade_type,position)
                                    # last trade was buy5,buy6  --> sell4
                                    elif vol_last_trade_type[stock] == 'buy5' or vol_last_trade_type[stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'f')
                                            sellFunc(stock, last, 'sell4', buy_left, sell_left, vol_last_trade_type,position)
                                # price is at 5th interval
                                elif range_index == 4:
                                    # last trade was sell1，sell2  --> buy4
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[stock] == 'sell2':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'g')
                                            buyFunc(stock, last, 'buy4', False, buy_left, vol_last_trade_type,position)
                                # price is at 6th interval
                                elif range_index == 5:
                                    # last trade was sell1，sell2，buy2,sell3,buy3,sell4  --> buy5
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[
                                        stock] == 'sell2' or vol_last_trade_type[stock] == 'buy2' or \
                                                    vol_last_trade_type[stock] == 'sell3' or vol_last_trade_type[
                                        stock] == 'buy3' or vol_last_trade_type[stock] == 'sell4':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'h')
                                            buyFunc(stock, last, 'buy5', False, buy_left, vol_last_trade_type,position)
                                # price is at 7th interval
                                elif range_index == 6:
                                    # last trade was sell1，sell2，buy2,sell3,buy3,sell4，buy4,sell5,buy5  --> buy6
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[
                                        stock] == 'sell2' or vol_last_trade_type[stock] == 'buy2' or \
                                                    vol_last_trade_type[stock] == 'sell3' or vol_last_trade_type[
                                        stock] == 'buy3' or vol_last_trade_type[stock] == 'sell4' or \
                                                    vol_last_trade_type[stock] == 'buy4' or vol_last_trade_type[
                                        stock] == 'sell5' or vol_last_trade_type[stock] == 'buy5':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'i')
                                            buyFunc(stock, last, 'buy6', True, buy_left, vol_last_trade_type,position)
                            # up intervals open
                            elif vol_up_open_flag[stock] == True:
                                for r in stock_vol_range_up[stock]:
                                    if r[0] > last and last >= r[1]:
                                        range_index = stock_vol_range_up[stock].index(r)
                                        break
                                # price is at 1st interval
                                if range_index == 0:
                                    # last trade was sell2, buy2, buy3  --> sell1
                                    if vol_last_trade_type[stock] == 'sell2' or vol_last_trade_type[stock] == 'buy2' or \
                                                    vol_last_trade_type[
                                                        stock] == 'buy3':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'j')
                                            sellFunc(stock, last, 'sell1', buy_left, sell_left, vol_last_trade_type,position)
                                # price is at 2nd interval
                                elif range_index == 1:
                                    # last trade was buy3  --> sell2
                                    if vol_last_trade_type[stock] == 'buy3':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'k')
                                            sellFunc(stock, last, 'sell2', buy_left, sell_left, vol_last_trade_type,position)
                                # price is at 3rd interval
                                elif range_index == 2:
                                    # last trade was sell1  --> buy2
                                    if vol_last_trade_type[stock] == 'sell1':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'l')
                                            buyFunc(stock, last, 'buy2', False, buy_left, vol_last_trade_type,position)
                                # price is at 4th interval
                                elif range_index == 3:
                                    # last trade was sell1，sell2,buy2  --> buy3
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[
                                        stock] == 'sell2' or vol_last_trade_type[stock] == 'buy2':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'm')
                                            buyFunc(stock, last, 'buy3', False, buy_left, vol_last_trade_type,position)
                                # price is at 5th interval
                                elif range_index == 4:
                                    # buy5，open down interval
                                    if checkWeimai(stock) == True:
                                        print(stock, 'n')
                                        buyFunc(stock, last, 'buy5', False, buy_left, vol_last_trade_type,position)
                                        vol_down_open_flag[stock] = True

                            # down intervals open
                            elif vol_down_open_flag[stock] == True:
                                for r in stock_vol_range_down[stock]:
                                    if r[0] > last and last >= r[1]:
                                        range_index = stock_vol_range_down[stock].index(r)
                                        break
                                # price is at 1st interval
                                if range_index == 0:
                                    # sell2,open up interval
                                    if checkWeimai(stock) == True:
                                        print(stock, 'o')
                                        sellFunc(stock, last, 'sell2', buy_left, sell_left, vol_last_trade_type,position)
                                        vol_up_open_flag[stock] = True

                                # price is at 2nd interval
                                elif range_index == 1:
                                    # last trade was buy5,buy6  --> sell4
                                    if vol_last_trade_type[stock] == 'buy5' or vol_last_trade_type[
                                        stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'p')
                                            sellFunc(stock, last, 'sell4', buy_left, sell_left, vol_last_trade_type,position)

                                # price is at 3rd interval
                                elif range_index == 2:
                                    # last trade was buy6  --> sell5
                                    if vol_last_trade_type[stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'q')
                                            sellFunc(stock, last, 'sell5', buy_left, sell_left, vol_last_trade_type,position)

                                # price is at 4th interval
                                elif range_index == 3:
                                    # last trade was sell4  --> buy5
                                    if vol_last_trade_type[stock] == 'sell4':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'r')
                                            buyFunc(stock, last, 'buy5', False, buy_left, vol_last_trade_type,position)

                                # price is at 5th interval
                                elif range_index == 4:
                                    # last trade was sell4,sell5,buy5  --> buy6
                                    if vol_last_trade_type[stock] == 'sell4' or vol_last_trade_type[
                                        stock] == 'sell5' or vol_last_trade_type[stock] == 'buy5':
                                        if checkWeimai(stock) == True:
                                            print(stock, 's')
                                            buyFunc(stock, last, 'buy6', True, buy_left, vol_last_trade_type,position)
                            # all intervals close
                            else:
                                # above 2nd line，open up interval
                                if last >= stock_vol[stock][0]:
                                    if checkWeimai(stock) == True:
                                        print(stock, 't')
                                        sellFunc(stock, last, 'sell2', buy_left, sell_left, vol_last_trade_type,position)
                                        vol_up_open_flag[stock] = True
                                        updateRangesFromUp(stock_vol_abs[stock], last * 0.998, stock,
                                                           stock_vol_range_all, stock_vol_range_up,
                                                           stock_vol_range_down)
                                        print("update 2")
                                        print(stock_vol_range_all)
                                        print(stock_vol_range_up)
                                        print(stock_vol_range_down)
                                # below 5th line,open down interval
                                elif last < stock_vol[stock][1]:
                                    if checkWeimai(stock) == True:
                                        if (last - zhisun_p) / zhisun_p >= 0.02:
                                            print(stock, 'u')
                                            buyFunc(stock, last, 'buy5', False, buy_left, vol_last_trade_type,position)
                                            vol_down_open_flag[stock] = True
                                            updateRangesFromDown(stock_vol_abs[stock], last * 1.002, stock,
                                                                 stock_vol_range_all, stock_vol_range_up,
                                                                 stock_vol_range_down)
                                            print("update 3")
                                            print(stock_vol_range_all)
                                            print(stock_vol_range_up)
                                            print(stock_vol_range_down)

                stock_conf.to_csv(stock_config_file, index=False)
                print('DONE this minute')
                w.stop()
        sleep(57)
        a += 1
        # print(a)
        REGISTRY = pickle.dumps(a)


if __name__ == '__main__':
    print("To stop the script execution type CTRL-C")
    while 1:
        start = pickle.loads(REGISTRY) if REGISTRY else 0
        try:
            main(start=start)

        except KeyboardInterrupt:
            resume = input('If you want to continue type the letter c:')
            stock_conf.to_csv(stock_config_file, index=False)
            if resume != 'c':
                break
            # else:
            #
            #     print(vol)
