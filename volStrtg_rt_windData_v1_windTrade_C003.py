# coding=utf-8
from WindPy import *
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import math
import pickle
import logging
logging.basicConfig(filename='windTrade_C003.log',level=logging.DEBUG)

pd.set_option('expand_frame_repr', False)


class OpenTradeObj(object):
    trade_type = ''
    order_id = ''
    order_quantity = 0


###########################round to 100################
def truncate(f, n):
    '''Truncates/pads a int f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d + '0' * n)[:n]])


############################upper interval has been opened, update all intervals############################
def updateRangesFromUp(vol_abs, price, stock):
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
    global stock_vol_range_all, stock_vol_range_up, stock_vol_range_down
    stock_vol_range_all[stock] = all_range_vol
    stock_vol_range_up[stock] = up_range_vol
    stock_vol_range_down[stock] = down_range_vol


############################lower interval has been opened, update all intervals############################

def updateRangesFromDown(vol_abs, price, stock):
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

    global stock_vol_range_all,stock_vol_range_up,stock_vol_range_down
    stock_vol_range_all[stock] = all_range_vol
    stock_vol_range_up[stock] = up_range_vol
    stock_vol_range_down[stock] = down_range_vol


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


def getStockPositionWind(position_data, stock):
    if 'SecurityCode' not in position_data.columns:
        return 0
    stocks = list(position_data['SecurityCode'].values)
    if stock in stocks:
        try:
            position = int((position_data.loc[(position_data['SecurityCode'] == stock)])['SecurityVolume'].values[0])
        except:
            print ('got position except for stock ' + stock)
            return 0
    else:
        position = 0
    return position


def getStockEachTradeQuantity(stock):
    global stock_conf
    EachStockTradeQuantity = (stock_conf.loc[(stock_conf['Stock'] == stock)])['EachStockTradeQuantity'].values[0]
    return int(EachStockTradeQuantity)




def getStockSellable(stock, position):
    global daily_start_position
    start_position = getStockPositionWind(daily_start_position, stock)
    sellable = start_position
    if position < start_position:
        sellable = sellable - (start_position - position)
    return sellable


def getFirstTimeBuyFactor(stock):
    global stock_conf
    FirstTimeBuyFactor = (stock_conf.loc[(stock_conf['Stock'] == stock)])['FirstTimeBuyFactor'].values[0]
    return float(FirstTimeBuyFactor)


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
def sellFunc(stock, last, sellType,  position):
    global sell_left
    if sell_left[stock] > 0:
        each_stock_trade_quantity = getStockEachTradeQuantity(stock)
        sellable = getStockSellable(stock, position)
        trade_quantity = min(sellable, each_stock_trade_quantity)
        trade_quantity = int(float(truncate(trade_quantity / 100, 0)) * 100)
        print("should sell ", str(trade_quantity), ', sell type: ', sellType)
        logging.debug("should sell " + str(trade_quantity) + ', sell type: '+ sellType)
        trade_price = last * 0.998

        status = placeOrder(stock, trade_price, trade_quantity, "Sell", sellType)
        if status == 'Success':
            print(stock, ' success place sell order')
            logging.debug(stock + ' success place sell order')
        elif status == 'Failed':
            print(stock, ' failed place sell order')
            logging.debug(stock + ' failed place sell order')
    else:
        print("no more sell left")
        logging.debug("no more sell left")

##############################buy function######################
def buyFunc(stock, last, buyType, isDouble):
    global buy_left
    if buy_left[stock] > 0:
        each_stock_trade_quantity = getStockEachTradeQuantity(stock)
        if isDouble == True:
            trade_quantity = each_stock_trade_quantity * 2
        else:
            trade_quantity = each_stock_trade_quantity
        trade_quantity = int(float(truncate(trade_quantity / 100, 0)) * 100)
        print(buyType)
        logging.debug(buyType)
        trade_price = last * 1.002

        status = placeOrder(stock, trade_price, trade_quantity, "Buy", buyType)
        if status == 'Success':
            print(stock, ' success place buy order')
            logging.debug(stock + ' success place buy order')
        elif status == 'Failed':
            print(stock, ' failed place buy order')
            logging.debug(stock + ' failed place buy order')
    else:
        print("no more buy left")
        logging.debug("no more buy left")


##############################buy first trade function######################
def buyFirstFunc(stock, last):
    # global stock_conf
    # stocks = list(stock_conf['Stock'].values)
    number_of_stocks = 10 #len(stocks)
    firstTimeBuyFactor = getFirstTimeBuyFactor(stock)
    global cash
    buy_cash = cash / number_of_stocks * firstTimeBuyFactor   # use half of the cash to buy
    trade_price = last * 1.002
    trade_quantity = buy_cash / trade_price
    if trade_quantity < 400:
        trade_quantity = 400
    trade_quantity = int(float(truncate(trade_quantity / 100, 0)) * 100)

    status = placeOrder(stock, trade_price, trade_quantity, "Buy", "FirstTime")
    if status == 'Success':
        print(stock, ' success place order first time')
        logging.debug(stock + ' success place order first time')
    elif status == 'Failed':
        print(stock, ' failed place order first time')
        logging.debug(stock + ' failed place order first time')





##############################Place an order##############################
def placeOrder(stock, trade_price, trade_quantity, side, type):
    order_data = conWSDData(w.torder(stock, side, trade_price, trade_quantity, "OrderType=LMT;LogonID=1"))
    request_id = str(order_data['RequestID'].values[0])
    if len(request_id) == 0:
        print ('request id is empty,place order failed')
        return 'Failed'
    sleep(2)
    ####get order id by request id####
    query_data = conWSDData(w.tquery('Order', 'LogonID=1;RequestID=' + request_id))
    wait_try_ct = 0
    while 'OrderNumber' not in query_data.columns and wait_try_ct < 3:
        wait_try_ct = wait_try_ct + 1
        print ('not find just placed order')
        print (str(query_data['ErrorMsg'].values[0]))
        print ('requestid: ' + request_id)
        query_data = conWSDData(w.tquery('Order', 'LogonID=1;RequestID=' + request_id))
        sleep (2)
    if 'OrderNumber' in query_data.columns:
        order_id = str(query_data['OrderNumber'].values[0])
    else:
        print ('failed place order, no order number, ignore the trade')
        return 'Failed'

    open_trade_obj = OpenTradeObj()
    open_trade_obj.trade_type = type
    open_trade_obj.order_id = order_id
    open_trade_obj.order_quantity = trade_quantity

    global open_trade_dict
    open_trade_dict[stock] = open_trade_obj
    return 'Success'




#################################check open trade status from wind#############
def checkOpenTradeStatus(open_trade_obj, stock):
    order_id = open_trade_obj.order_id
    order_quantity = open_trade_obj.order_quantity

    query_data = conWSDData(w.tquery('Order', 'LogonID=1;OrderNumber=' + order_id))
    # order_volume = int(query_data['OrderVolume'].values[0])
    traded_volume = int(query_data['TradedVolume'].values[0])

    if traded_volume != order_quantity:
        remark = str(query_data['Remark'].values[0])
        print('成交量与下单量不符合！order number: ', order_id)
        print('remark: ', remark)
        if remark == '废单':
            print ('废单，从open trade obj中删除')
            logging.debug('废单，从open trade obj中删除')
            open_trade_dict.pop(stock)
            return 'OK'
        logging.debug('成交量与下单量不符合！order number: '+ order_id)
        logging.debug('remark: '+ remark)
        return 'NOT OK'
    else:
        global vol_last_trade_type, buy_left, sell_left
        vol_last_trade_type[stock] = open_trade_obj.trade_type

        if open_trade_obj.trade_type.startswith('buy'):
            buy_left[stock] = buy_left[stock] - 1
        elif open_trade_obj.trade_type.startswith('sell'):
            sell_left[stock] = sell_left[stock] - 1
            buy_left[stock] = buy_left[stock] + 1

        elif open_trade_obj.trade_type == 'FirstTime':
            each_trade_quantity = traded_volume / 4
            each_trade_quantity = int(float(truncate(each_trade_quantity / 100, 0)) * 100)
            updateConfig(stock, ["EachStockTradeQuantity"], [each_trade_quantity])
        # else:
        #     updateConfig(stock, ["EachStockTradeQuantity"], [traded_volume])
        open_trade_dict.pop(stock)
        return 'OK'


###############################Load config info from file#####################
def loadConfig():
    global stock_conf
    stock_conf = pd.read_csv(stock_config_file, dtype=str)
    ####### get all stocks####################
    stocks = list(stock_conf['Stock'].values)
    for stock in stocks:
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


#####################initialize variables############################
data_dir = "C:\KeLiQuant\\"
stock_config_file = data_dir + 'stock_conf_wind_test_C003.txt'
zhisun_stock_temp = []
special_zhisun_price = {}
special_zhisun_day = {}
cash = 10000000

first_time = {}
stock_exec_flag = {}
stock_vol_range_all = {}
stock_vol_range_up = {}
stock_vol_range_down = {}
stock_vol = {}
stock_vol_abs = {}
vol_up_open_flag = {}
vol_down_open_flag = {}
vol_last_trade_type = {}
sell_left = {}
buy_left = {}
stock_conf = pd.DataFrame
daily_start_position = pd.DataFrame
open_trade_dict = {}
REGISTRY = None
prev_t_day = ''

junk_ct = 0
#########################################Start##########################################################################
def main(start=0):
    a = start
    global REGISTRY
    while 1:
        weekno = datetime.today().weekday()
        global junk_ct
        junk_ct = junk_ct + 1
        if weekno in [0, 1, 2, 3, 4]:  # should be [0,1,2,3,4]
            date_time = datetime.today().strftime('%Y-%m-%d %H-%M')
            today = date_time.split(' ')[0]
            ###########################
            curTime = date_time.split(' ')[1]
            ####################################before trading daily#############################################################
            if curTime == '08-00':
                w.start()
                w.tlogon("0000", "0", "W124041900401", "********", "SHSZ")
                global daily_start_position
                daily_start_position = conWSQData(w.tquery('Position', 'LogonID=1'))
                w.tlogout(LogonID=1)
                loadConfig()
                global prev_t_day
                prev_t_day = getTDays(-1,
                                      today)  # if today is weekend, then previous 1 trading day would be Thursday, treat weekends as Friday

                print("today is : ", today)
                print("previous trading day is : ", prev_t_day)

                logging.debug("today is : " + str(today))
                logging.debug("previous trading day is : " + str(prev_t_day))
                global stock_conf
                stocks = list(stock_conf['Stock'].values)

                for stock in stocks:
                    print(stock)
                    logging.debug(stock)
                    ###################Special zhi sun strategy##########################
                    if stock in special_zhisun_day.keys():
                        teshu_zhisun_day = str(special_zhisun_day[stock])
                        special_zhisun_price[stock] = float(w.wsd(stock, "MA", prev_t_day, prev_t_day,
                                                                  "MA_N=" + teshu_zhisun_day + ";Fill=Previous;PriceAdj=F").Data[
                                                                0][-1])
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
                    volUp2 = price_close_vol[-1] + vol_abs
                    volDown5 = price_close_vol[-1] - vol_abs

                    stock_vol.setdefault(stock, [])
                    stock_vol[stock] = []
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
                    sleep(1)
                w.tlogout(LogonID=1)
                w.stop()
                print(stock_vol)
                print("DONE daily before trading process")
                logging.debug(stock_vol)
                logging.debug("DONE daily before trading process")
            ###########################################################trading#####################################################################
            elif (curTime >= '09-30' and curTime <= '11-30') or (curTime >= '13-00' and curTime <= '15-00'):
                w.start()
                print('START this minute ', curTime)
                logging.debug('START this minute '+ curTime)
                w.tlogon("0000", "0", "W124041900401", "********", "SHSZ")
                try:
                    curAllStockPosition = conWSQData(w.tquery('Position', 'LogonID=1'))
                except:
                    print ('got current stock position except')
                    continue

                # load config file every minute, file has most updated info
                loadConfig()

                stocks = list(stock_conf['Stock'].values)
                for stock in stocks:
                    try:
                        print (stock)
                        logging.debug(stock)
                        wdata = w.wsq(stock, 'rt_last')
                        try:
                            last = float(wdata.Data[0][0])
                        except:
                            print ('got price data exception')
                            continue
                        position = getStockPositionWind(curAllStockPosition, stock)
                        #####check for open trade
                        if stock in open_trade_dict.keys():
                            res = checkOpenTradeStatus(open_trade_dict[stock], stock)
                            if res == 'NOT OK':
                                print(stock, ' has not traded enough, continue to next stock')
                                logging.debug(stock + ' has not traded enough, continue to next stock')
                                continue
                        # if zhisun happened, abandon this stock
                        if position == 0 and stock in zhisun_stock_temp:
                            stock_conf = stock_conf[stock_conf.Stock != stock]
                            zhisun_stock_temp.remove(stock)
                            continue
                        # first time, force to buy
                        if position == 0 and first_time[stock] == True:
                            print(stock, ' buy first time')
                            logging.debug(stock + ' buy first time')
                            buyFirstFunc(stock, last)
                            stock_exec_flag[stock] = False  # start volatility trade next day
                            first_time[stock] = False
                            continue

                        # special zhisun
                        if stock in special_zhisun_price.keys():
                            if last <= special_zhisun_price[stock]:
                                if stock not in zhisun_stock_temp:
                                    zhisun_stock_temp.append(stock)
                                print("sell - special zhi sun ", stock)
                                logging.debug("sell - special zhi sun "+ stock)

                        # Get zhisun (zhisun_day or zhisun_price)
                        isFixZhisun = getIsFixedZhisunPrice(stock)
                        if isFixZhisun == True:
                            zhisun_p = getZhisunPrice(stock)
                        else:
                            # prev_t_day = getTDays(-1, today)
                            zhisun_day = getZhisunDay(stock)
                            zhisun_p = float(w.wsd(stock, "MA", prev_t_day, prev_t_day,
                                                   "MA_N=" + str(zhisun_day) + ";Fill=Previous;PriceAdj=F").Data[0][-1])
                        # fixed price zhisun
                        if last <= zhisun_p or stock in zhisun_stock_temp:
                            print("sell - zhi sun ", stock)
                            logging.debug("sell - zhi sun "+ stock)
                            sellable = getStockSellable(stock, position)
                            trade_price = last * 0.998
                            placeOrder(stock, trade_price, sellable, "Sell", 'zhisun')
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
                                            logging.debug(stock+ 'a')
                                            sellFunc(stock, last, 'sell1', position)
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
                                            logging.debug(stock+ 'b')
                                            sellFunc(stock, last, 'sell2', position)
                                # price is at 3rd interval
                                elif range_index == 2:
                                    # last trade was sell1  --> buy2
                                    if vol_last_trade_type[stock] == 'sell1':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'c')
                                            logging.debug(stock+'c')
                                            buyFunc(stock, last, 'buy2', False)
                                    # last trade was buy5,buy6  --> sell3
                                    elif vol_last_trade_type[stock] == 'buy5' or vol_last_trade_type[stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'd')
                                            logging.debug(stock+ 'd')
                                            sellFunc(stock, last, 'sell3', position)
                                # price is at 4th interval
                                elif range_index == 3:
                                    # last trade was sell1，sell2 --> buy3
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[stock] == 'sell2':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'e')
                                            logging.debug(stock+ 'e')
                                            buyFunc(stock, last, 'buy3', False)
                                    # last trade was buy5,buy6  --> sell4
                                    elif vol_last_trade_type[stock] == 'buy5' or vol_last_trade_type[stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'f')
                                            logging.debug(stock+ 'f')
                                            sellFunc(stock, last, 'sell4', position)
                                # price is at 5th interval
                                elif range_index == 4:
                                    # last trade was sell1，sell2  --> buy4
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[stock] == 'sell2':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'g')
                                            logging.debug(stock+ 'g')
                                            buyFunc(stock, last, 'buy4', False)
                                # price is at 6th interval
                                elif range_index == 5:
                                    # last trade was sell1，sell2，buy2,sell3,buy3,sell4  --> buy5
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[
                                        stock] == 'sell2' or vol_last_trade_type[stock] == 'buy2' or \
                                                    vol_last_trade_type[stock] == 'sell3' or vol_last_trade_type[
                                        stock] == 'buy3' or vol_last_trade_type[stock] == 'sell4':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'h')
                                            logging.debug(stock+ 'h')
                                            buyFunc(stock, last, 'buy5', False)
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
                                            logging.debug(stock+ 'i')
                                            buyFunc(stock, last, 'buy6', False)
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
                                            logging.debug(stock+ 'j')
                                            sellFunc(stock, last, 'sell1', position)
                                # price is at 2nd interval
                                elif range_index == 1:
                                    # last trade was buy3  --> sell2
                                    if vol_last_trade_type[stock] == 'buy3':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'k')
                                            logging.debug(stock+ 'k')
                                            sellFunc(stock, last, 'sell2', position)
                                # price is at 3rd interval
                                elif range_index == 2:
                                    # last trade was sell1  --> buy2
                                    if vol_last_trade_type[stock] == 'sell1':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'l')
                                            logging.debug(stock+ 'l')
                                            buyFunc(stock, last, 'buy2', False)
                                # price is at 4th interval
                                elif range_index == 3:
                                    # last trade was sell1，sell2,buy2  --> buy3
                                    if vol_last_trade_type[stock] == 'sell1' or vol_last_trade_type[
                                        stock] == 'sell2' or vol_last_trade_type[stock] == 'buy2':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'm')
                                            logging.debug(stock+ 'm')
                                            buyFunc(stock, last, 'buy3', False)
                                # price is at 5th interval
                                elif range_index == 4:
                                    # buy5，open down interval
                                    if checkWeimai(stock) == True:
                                        print(stock, 'n')
                                        logging.debug(stock+ 'n')
                                        buyFunc(stock, last, 'buy5', False)
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
                                        logging.debug(stock+ 'o')
                                        sellFunc(stock, last, 'sell2', position)
                                        vol_up_open_flag[stock] = True

                                # price is at 2nd interval
                                elif range_index == 1:
                                    # last trade was buy5,buy6  --> sell4
                                    if vol_last_trade_type[stock] == 'buy5' or vol_last_trade_type[
                                        stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'p')
                                            logging.debug(stock+ 'p')
                                            sellFunc(stock, last, 'sell4', position)

                                # price is at 3rd interval
                                elif range_index == 2:
                                    # last trade was buy6  --> sell5
                                    if vol_last_trade_type[stock] == 'buy6':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'q')
                                            logging.debug(stock+ 'q')
                                            sellFunc(stock, last, 'sell5', position)

                                # price is at 4th interval
                                elif range_index == 3:
                                    # last trade was sell4  --> buy5
                                    if vol_last_trade_type[stock] == 'sell4':
                                        if checkWeimai(stock) == True:
                                            print(stock, 'r')
                                            logging.debug(stock+ 'r')
                                            buyFunc(stock, last, 'buy5', False)

                                # price is at 5th interval
                                elif range_index == 4:
                                    # last trade was sell4,sell5,buy5  --> buy6
                                    if vol_last_trade_type[stock] == 'sell4' or vol_last_trade_type[
                                        stock] == 'sell5' or vol_last_trade_type[stock] == 'buy5':
                                        if checkWeimai(stock) == True:
                                            print(stock, 's')
                                            logging.debug(stock+ 's')
                                            buyFunc(stock, last, 'buy6', False)
                            # all intervals close
                            else:
                                # above 2nd line，open up interval
                                if last >= stock_vol[stock][0]:
                                    if checkWeimai(stock) == True:
                                        print(stock, 't')
                                        logging.debug(stock+ 't')
                                        sellFunc(stock, last, 'sell2', position)
                                        vol_up_open_flag[stock] = True
                                        updateRangesFromUp(stock_vol_abs[stock], last * 0.998, stock)
                                        print("update 2")
                                        print(stock_vol_range_all)
                                        print(stock_vol_range_up)
                                        print(stock_vol_range_down)

                                        logging.debug("update 2")
                                        logging.debug(stock_vol_range_all)
                                        logging.debug(stock_vol_range_up)
                                        logging.debug(stock_vol_range_down)
                                # below 5th line,open down interval
                                elif last < stock_vol[stock][1]:
                                    if checkWeimai(stock) == True:
                                        if (last - zhisun_p) / zhisun_p >= 0.02:
                                            print(stock, 'u')
                                            logging.debug(stock+ 'u')
                                            buyFunc(stock, last, 'buy5', False)
                                            vol_down_open_flag[stock] = True
                                            updateRangesFromDown(stock_vol_abs[stock], last * 1.002, stock)
                                            print("update 3")
                                            print(stock_vol_range_all)
                                            print(stock_vol_range_up)
                                            print(stock_vol_range_down)

                                            logging.debug("update 3")
                                            logging.debug(stock_vol_range_all)
                                            logging.debug(stock_vol_range_up)
                                            logging.debug(stock_vol_range_down)
                    except:
                        print ('except in big loop')
                        continue
                stock_conf.to_csv(stock_config_file, index=False)
                print('DONE this minute')
                logging.debug('DONE this minute')
                w.tlogout(LogonID=1)
                w.stop()
            # else:
            #     print ('sleeping')
        # else:
        #     print ('sleeping')
        sleep(5)
        print (junk_ct)
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
            stock_conf.to_csv(stock_config_file, index=False)
            resume = input('If you want to continue type the letter c:')
            if resume != 'c':
                break
                # else:
                #
                #     print(vol)
