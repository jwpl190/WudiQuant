# coding=utf-8
# 把中间变量都存到文件中，可随时停止程序
from WindPy import *
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import math
import pickle
import logging

logging.basicConfig(filename='windTrade_C003.log', level=logging.DEBUG)

pd.set_option('expand_frame_repr', False)

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

    updateConfig(stock, ["VolUp1", "VolUp2", "VolUp3", "VolDown4","VolDown5","VolDown6"],
                 [volUp1, volUp2, volUp3, volDown4,volDown5,volDown6])


############################lower interval has been opened, update all intervals############################

def updateRangesFromDown(vol_abs, price, stock):
    volUp1 = price + vol_abs * 2.5
    volUp2 = price + vol_abs * 2
    volUp3 = price + vol_abs * 1.5

    volDown4 = price + vol_abs * 0.5
    volDown5 = price
    volDown6 = price - vol_abs * 0.5

    updateConfig(stock, ["VolUp1", "VolUp2", "VolUp3", "VolDown4", "VolDown5", "VolDown6"],
                 [volUp1, volUp2, volUp3, volDown4, volDown5, volDown6])

############################get all range############################
def getRangeAll(stock):
    volUp1 = getVolUp1(stock)
    volUp2 = getVolUp2(stock)
    volUp3 = getVolUp3(stock)
    volDown4 = getVolDown4(stock)
    volDown5 = getVolDown5(stock)
    volDown6 = getVolDown6(stock)

    # (aaa,bbb]
    all_range_vol = [(sys.float_info.max, volUp1), (volUp1, volUp2), (volUp2, volUp3), (volUp3, volDown4),
                     (volDown4, volDown5), (volDown5, volDown6), (volDown6, sys.float_info.min)]

    return all_range_vol
############################get up range############################
def getRangeUp(stock):
    volUp1 = getVolUp1(stock)
    volUp2 = getVolUp2(stock)
    volUp3 = getVolUp3(stock)
    volDown5 = getVolDown5(stock)

    # (aaa,bbb]
    up_range_vol = [(sys.float_info.max, volUp1), (volUp1, volUp2), (volUp2, volUp3), (volUp3, volDown5),
                    (volDown5, sys.float_info.min)]

    return up_range_vol
############################get down range############################
def getRangeDown(stock):
    volUp2 = getVolUp2(stock)
    volDown4 = getVolDown4(stock)
    volDown5 = getVolDown5(stock)
    volDown6 = getVolDown6(stock)
    # (aaa,bbb]
    down_range_vol = [(sys.float_info.max, volUp2), (volUp2, volDown4), (volDown4, volDown5), (volDown5, volDown6),
                      (volDown6, sys.float_info.min)]

    return down_range_vol
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

def getOpenTradePrice(stock):
    global stock_conf
    open_trade_price = (stock_conf.loc[(stock_conf['Stock'] == stock)])['OpenTradePrice'].values[0]
    return float(open_trade_price)

def getOpenTradeId(stock):
    global stock_conf
    open_trade_id = (stock_conf.loc[(stock_conf['Stock'] == stock)])['OpenTradeId'].values[0]
    return str(open_trade_id)

def getZhisunFlag(stock):
    global stock_conf
    zhi_sun_flag = (stock_conf.loc[(stock_conf['Stock'] == stock)])['ZhisunFlag'].values[0]
    return str(zhi_sun_flag)

def getDailyStartPosition(stock):
    global stock_conf
    daily_s_pos = (stock_conf.loc[(stock_conf['Stock'] == stock)])['DailyStartPosition'].values[0]
    return int(daily_s_pos)

def getFirstTimeBuyFactor(stock):
    global stock_conf
    first_time_buy_factor = (stock_conf.loc[(stock_conf['Stock'] == stock)])['FirstTimeBuyFactor'].values[0]
    return float(first_time_buy_factor)


def getStockPositionWind(position_data, stock):
    if 'SecurityCode' not in position_data.columns:
        return 0
    stocks = list(position_data['SecurityCode'].values)
    if stock in stocks:
        try:
            position = int((position_data.loc[(position_data['SecurityCode'] == stock)])['SecurityVolume'].values[0])
        except:
            print('got position except for stock ' + stock)
            logging.debug('got position except for stock ' + stock)
            return 0
    else:
        position = 0
    return position


def getStockSellable(stock, position):
    daily_start_position = getDailyStartPosition(stock)
    sellable = daily_start_position
    if position < daily_start_position:
        sellable = sellable - (daily_start_position - position)
    return sellable


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
def sellFunc(stock, last, sellType, position):
    sell_left = getSellLeft(stock)
    if sell_left > 0:
        each_stock_trade_quantity = getStockEachTradeQuantity(stock)
        sellable = getStockSellable(stock, position)
        trade_quantity = min(sellable, each_stock_trade_quantity)
        trade_quantity = int(float(truncate(trade_quantity / 100, 0)) * 100)
        print("should sell ", str(trade_quantity), ', sell type: ', sellType)
        logging.debug("should sell " + str(trade_quantity) + ', sell type: ' + sellType)
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
    buy_left = getBuyLeft(stock)
    if buy_left > 0:
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
    number_of_stocks = 10  # len(stocks)
    firstTimeBuyFactor = getFirstTimeBuyFactor(stock)
    global cash
    buy_cash = cash / number_of_stocks * firstTimeBuyFactor  # use half of the cash to buy
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

##############################sell zhisun function######################
def sellZhisunFunc(stock, last, sellType,position):
    sellable = getStockSellable(stock, position)
    print("should sell ", str(sellable), ', sell type: ', sellType)
    logging.debug("should sell " + str(sellable) + ', sell type: ' + sellType)
    trade_price = last * 0.998
    updateConfig(stock, ["ZhisunFlag"], ['Y'])
    status = placeOrder(stock, trade_price, sellable, "Sell", sellType)
    if status == 'Success':
        print(stock, ' success place sell zhisun order')
        logging.debug(stock + ' success place sell zhisun order')
    elif status == 'Failed':
        print(stock, ' failed place sell zhisun order')
        logging.debug(stock + ' failed place sell zhisun order')



##############################Place an order##############################
def placeOrder(stock, trade_price, trade_quantity, side, order_type):
    order_data = conWSDData(w.torder(stock, side, trade_price, trade_quantity, "OrderType=LMT;LogonID=1"))
    request_id = str(order_data['RequestID'].values[0])
    if len(request_id) == 0:
        print('request id is empty,place order failed')
        return 'Failed'
    sleep(2)
    ####get order id by request id####
    query_data = conWSDData(w.tquery('Order', 'LogonID=1;RequestID=' + request_id))
    wait_try_ct = 0
    while 'OrderNumber' not in query_data.columns and wait_try_ct < 3:
        wait_try_ct = wait_try_ct + 1
        print('not find just placed order')
        print(str(query_data['ErrorMsg'].values[0]))
        print('requestid: ' + request_id)
        query_data = conWSDData(w.tquery('Order', 'LogonID=1;RequestID=' + request_id))
        sleep(2)
    if 'OrderNumber' in query_data.columns:
        order_id = str(query_data['OrderNumber'].values[0])
    else:
        print('failed place order, no order number, ignore the trade')
        return 'Failed'

    updateConfig(stock, ["OpenTradeType", "OpenTradeQuantity", "OpenTradePrice", "OpenTradeId"], [order_type, trade_quantity,trade_price, order_id])
    return 'Success'

##################################update open trade#############################
def updateOpenTradeFields(stock,o_type,o_quantity,o_price,o_id):
    updateConfig(stock, ["OpenTradeType", "OpenTradeQuantity", "OpenTradePrice", "OpenTradeId"],
                 [o_type, o_quantity, o_price, o_id])

#################################check open trade status from wind#############
def checkOpenTradeStatus(stock,open_trade_type):
    open_order_id = getOpenTradeId(stock)
    open_order_quantity = getOpenTradeQuantity(stock)
    open_order_price = getOpenTradePrice(stock)

    query_data = conWSDData(w.tquery('Order', 'LogonID=1;OrderNumber=' + open_order_id))
    # order_volume = int(query_data['OrderVolume'].values[0])
    traded_volume = int(query_data['TradedVolume'].values[0])

    if traded_volume != open_order_quantity:
        remark = str(query_data['Remark'].values[0])
        print('成交量与下单量不符合！order number: ', open_order_id)
        print('remark: ', remark)
        if remark == '废单':
            print('废单，更新config file')
            logging.debug('废单，更新config file')
            updateOpenTradeFields(stock,"NV", 0, 0.0, "0")
            return 'OK'
        logging.debug('成交量与下单量不符合！order number: ' + open_order_id)
        logging.debug('remark: ' + remark)
        return 'NOT OK'
    else:
        if '-' in open_trade_type:  #sell2-openUp, buy5-openDown
            parsed_open_trade_type = open_trade_type.split('-')[0]
            updateConfig(stock, ["LastTradeType"], [parsed_open_trade_type])
        else:
            updateConfig(stock, ["LastTradeType"], [open_trade_type])

        if open_trade_type.startswith('buy'):
            buy_left = getBuyLeft(stock)
            buy_left = buy_left - 1
            updateConfig(stock, ["BuyLeft"], [buy_left])
        elif open_trade_type.startswith('sell'):
            buy_left = getBuyLeft(stock)
            buy_left = buy_left + 1
            sell_left = getSellLeft(stock)
            sell_left = sell_left - 1
            updateConfig(stock, ["BuyLeft", "SellLeft"], [buy_left, sell_left])

        if open_trade_type == 'FirstTime':
            each_trade_quantity = traded_volume / 4
            each_trade_quantity = int(float(truncate(each_trade_quantity / 100, 0)) * 100)
            updateConfig(stock, ["EachStockTradeQuantity"], [each_trade_quantity])
        elif open_trade_type == 'sell2-openUp':
            vol_abs = getVolAbs(stock)
            updateRangesFromUp(vol_abs, open_order_price, stock)
            updateConfig(stock, ["UpOpenFlag"],
                         ['Open'])
        elif open_trade_type == 'buy5-openDown':
            vol_abs = getVolAbs(stock)
            updateRangesFromDown(vol_abs,open_order_price,stock)
            updateConfig(stock, ["DownOpenFlag"],
                         ['Open'])
        updateOpenTradeFields(stock,"NV", 0, 0.0, "0")
        return 'OK'


###############################Load config info from file#####################
def loadConfig():
    global stock_conf
    stock_conf = pd.read_csv(stock_config_file, dtype=str)

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
data_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/"
stock_config_file = data_dir + 'stock_conf_wind_test_C003_v2.csv'
cash = 10000000
stock_conf = pd.DataFrame


#########################################Start##########################################################################
def main():
    while 1:
        weekno = datetime.today().weekday()
        if weekno in [0, 1, 2, 3, 4]:  # should be [0,1,2,3,4]
            date_time = datetime.today().strftime('%Y-%m-%d %H-%M')
            curTime = date_time.split(' ')[1]
            ###########################################################trading#####################################################################
            if (curTime >= '09-30' and curTime <= '11-30') or (curTime >= '13-00' and curTime <= '15-00'):
                w.start()
                print('START this minute ', date_time)
                logging.debug('START this minute ' + date_time)
                w.tlogon("0000", "0", "W124041900431", "********", "SHSZ")
                try:
                    curAllStockPosition = conWSQData(w.tquery('Position', 'LogonID=1'))
                except:
                    print('got current stock position except')
                    logging.debug('got current stock position except')
                    w.tlogout(LogonID=1)
                    w.stop()
                    sleep(2)
                    continue

                # load config file every minute, file has most updated info
                loadConfig()
                global stock_conf
                stocks = list(stock_conf['Stock'].values)
                parsedStock = parseStock(stocks)
                try:
                    last_price_data = w.wsq(parsedStock, 'rt_last')
                except:
                    print ('got current stocks price excep')
                    logging.debug('got current stocks price excep')
                    w.tlogout(LogonID=1)
                    w.stop()
                    sleep(2)
                    continue
                for i in range(0, len(last_price_data.Codes)):
                    stock = last_price_data.Codes[i]
                    last = last_price_data.Data[0][i]
                    print(stock)
                    logging.debug(stock)
                    position = getStockPositionWind(curAllStockPosition, stock)
                    #####check for open trade####
                    open_trade_type = getOpenTradeType(stock)
                    if open_trade_type != 'NV':
                        res = checkOpenTradeStatus(stock,open_trade_type)
                        if res == 'NOT OK':
                            print(stock, ' has not traded enough, continue to next stock')
                            logging.debug(stock + ' has not traded enough, continue to next stock')
                            continue
                    # if zhisun happened, abandon this stock
                    zhisun_flag = getZhisunFlag(stock)
                    if position == 0 and zhisun_flag == 'Y':
                        stock_conf = stock_conf[stock_conf.Stock != stock]
                        stock_conf.to_csv(stock_config_file, index=False)
                        continue
                    # first time, force to buy
                    exec_t_flag = getExecTFlag(stock)
                    # if position == 0 and exec_t_flag == 'N':
                    #     print(stock, ' buy first time')
                    #     logging.debug(stock + ' buy first time')
                    #     buyFirstFunc(stock, last)
                    #     stock_conf.to_csv(stock_config_file, index=False)
                    #     continue

                    # special zhisun
                    special_zhisun_flag = getSpecialZhisunFlag(stock)
                    if special_zhisun_flag == 'Y':
                        special_zhisun_price = getSpecialZhisunPrice(stock)
                        if last <= special_zhisun_price:
                            updateConfig(stock, ["ZhisunFlag"], ['Y'])
                            print("sell - special zhi sun ", stock)
                            logging.debug("sell - special zhi sun " + stock)

                    # Get zhisun price
                    zhisun_p = getZhisunPrice(stock)
                    if last <= zhisun_p or zhisun_flag == 'Y':
                        print("sell - zhi sun ", stock)
                        logging.debug("sell - zhi sun " + stock)
                        sellZhisunFunc(stock, last, 'zhisun', position)
                        stock_conf.to_csv(stock_config_file, index=False)
                        continue
                    # volatility strategy
                    if exec_t_flag == 'Y':
                        vol_up_open_flag = getUpRangeOpenFlag(stock)
                        vol_down_open_flag = getDownRangeOpenFlag(stock)
                        vol_last_trade_type = getLastTradeType(stock)
                        # all intervals open
                        if vol_up_open_flag == 'Open' and vol_down_open_flag == 'Open':
                            stock_vol_range_all = getRangeAll(stock)
                            for r in stock_vol_range_all:
                                if r[0] > last and last >= r[1]:
                                    range_index = stock_vol_range_all.index(r)
                                    break
                            # price is at 1st interval
                            if range_index == 0:
                                # last trade was sell2, buy2, sell3,buy3,sell4,buy4,sell5,buy5,buy6  --> sell1
                                if vol_last_trade_type == 'sell2' or vol_last_trade_type == 'buy2' or \
                                                vol_last_trade_type == 'sell3' or vol_last_trade_type == 'buy3' or \
                                                vol_last_trade_type == 'sell4' or vol_last_trade_type == 'buy4' or vol_last_trade_type == 'sell5' or \
                                                vol_last_trade_type == 'buy5' or vol_last_trade_type== 'buy6':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'a')
                                        logging.debug(stock + 'a')
                                        sellFunc(stock, last, 'sell1', position)
                            # price is at 2nd interval
                            elif range_index == 1:
                                # last trade was sell3,buy3,sell4,buy4,sell5,buy5,buy6  --> sell2
                                if vol_last_trade_type == 'sell3' or vol_last_trade_type== 'buy3' or vol_last_trade_type == 'sell4' or \
                                                vol_last_trade_type == 'buy4' or vol_last_trade_type == 'sell5' or vol_last_trade_type== 'buy5' or \
                                                vol_last_trade_type == 'buy6':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'b')
                                        logging.debug(stock + 'b')
                                        sellFunc(stock, last, 'sell2', position)
                            # price is at 3rd interval
                            elif range_index == 2:
                                # last trade was sell1  --> buy2
                                if vol_last_trade_type == 'sell1':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'c')
                                        logging.debug(stock + 'c')
                                        buyFunc(stock, last, 'buy2', False)
                                # last trade was buy5,buy6  --> sell3
                                elif vol_last_trade_type == 'buy5' or vol_last_trade_type == 'buy6':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'd')
                                        logging.debug(stock + 'd')
                                        sellFunc(stock, last, 'sell3', position)
                            # price is at 4th interval
                            elif range_index == 3:
                                # last trade was sell1，sell2 --> buy3
                                if vol_last_trade_type == 'sell1' or vol_last_trade_type== 'sell2':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'e')
                                        logging.debug(stock + 'e')
                                        buyFunc(stock, last, 'buy3', False)
                                # last trade was buy5,buy6  --> sell4
                                elif vol_last_trade_type == 'buy5' or vol_last_trade_type== 'buy6':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'f')
                                        logging.debug(stock + 'f')
                                        sellFunc(stock, last, 'sell4', position)
                            # price is at 5th interval
                            elif range_index == 4:
                                # last trade was sell1，sell2  --> buy4
                                if vol_last_trade_type == 'sell1' or vol_last_trade_type == 'sell2':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'g')
                                        logging.debug(stock + 'g')
                                        buyFunc(stock, last, 'buy4', False)
                            # price is at 6th interval
                            elif range_index == 5:
                                # last trade was sell1，sell2，buy2,sell3,buy3,sell4  --> buy5
                                if vol_last_trade_type == 'sell1' or vol_last_trade_type == 'sell2' or vol_last_trade_type == 'buy2' or \
                                                vol_last_trade_type == 'sell3' or vol_last_trade_type == 'buy3' or vol_last_trade_type == 'sell4':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'h')
                                        logging.debug(stock + 'h')
                                        buyFunc(stock, last, 'buy5', False)
                            # price is at 7th interval
                            elif range_index == 6:
                                # last trade was sell1，sell2，buy2,sell3,buy3,sell4，buy4,sell5,buy5  --> buy6
                                if vol_last_trade_type == 'sell1' or vol_last_trade_type == 'sell2' or vol_last_trade_type == 'buy2' or \
                                                vol_last_trade_type == 'sell3' or vol_last_trade_type == 'buy3' or vol_last_trade_type == 'sell4' or \
                                                vol_last_trade_type == 'buy4' or vol_last_trade_type== 'sell5' or vol_last_trade_type == 'buy5':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'i')
                                        logging.debug(stock + 'i')
                                        buyFunc(stock, last, 'buy6', False)
                        # up intervals open
                        elif vol_up_open_flag == 'Open':
                            stock_vol_range_up = getRangeUp(stock)
                            for r in stock_vol_range_up:
                                if r[0] > last and last >= r[1]:
                                    range_index = stock_vol_range_up.index(r)
                                    break
                            # price is at 1st interval
                            if range_index == 0:
                                # last trade was sell2, buy2, buy3  --> sell1
                                if vol_last_trade_type == 'sell2' or vol_last_trade_type == 'buy2' or \
                                                vol_last_trade_type == 'buy3':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'j')
                                        logging.debug(stock + 'j')
                                        sellFunc(stock, last, 'sell1', position)
                            # price is at 2nd interval
                            elif range_index == 1:
                                # last trade was buy3  --> sell2
                                if vol_last_trade_type == 'buy3':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'k')
                                        logging.debug(stock + 'k')
                                        sellFunc(stock, last, 'sell2', position)
                            # price is at 3rd interval
                            elif range_index == 2:
                                # last trade was sell1  --> buy2
                                if vol_last_trade_type == 'sell1':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'l')
                                        logging.debug(stock + 'l')
                                        buyFunc(stock, last, 'buy2', False)
                            # price is at 4th interval
                            elif range_index == 3:
                                # last trade was sell1，sell2,buy2  --> buy3
                                if vol_last_trade_type == 'sell1' or vol_last_trade_type == 'sell2' or vol_last_trade_type == 'buy2':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'm')
                                        logging.debug(stock + 'm')
                                        buyFunc(stock, last, 'buy3', False)
                            # price is at 5th interval
                            elif range_index == 4:
                                # buy5，open down interval
                                if checkWeimai(stock) == True:
                                    print(stock, 'n')
                                    logging.debug(stock + 'n')
                                    buyFunc(stock, last, 'buy5', False)


                        # down intervals open
                        elif vol_down_open_flag == 'Open':
                            stock_vol_range_down = getRangeDown(stock)
                            for r in stock_vol_range_down:
                                if r[0] > last and last >= r[1]:
                                    range_index = stock_vol_range_down.index(r)
                                    break
                            # price is at 1st interval
                            if range_index == 0:
                                # sell2,open up interval
                                if checkWeimai(stock) == True:
                                    print(stock, 'o')
                                    logging.debug(stock + 'o')
                                    sellFunc(stock, last, 'sell2', position)


                            # price is at 2nd interval
                            elif range_index == 1:
                                # last trade was buy5,buy6  --> sell4
                                if vol_last_trade_type == 'buy5' or vol_last_trade_type == 'buy6':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'p')
                                        logging.debug(stock + 'p')
                                        sellFunc(stock, last, 'sell4', position)

                            # price is at 3rd interval
                            elif range_index == 2:
                                # last trade was buy6  --> sell5
                                if vol_last_trade_type == 'buy6':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'q')
                                        logging.debug(stock + 'q')
                                        sellFunc(stock, last, 'sell5', position)

                            # price is at 4th interval
                            elif range_index == 3:
                                # last trade was sell4  --> buy5
                                if vol_last_trade_type == 'sell4':
                                    if checkWeimai(stock) == True:
                                        print(stock, 'r')
                                        logging.debug(stock + 'r')
                                        buyFunc(stock, last, 'buy5', False)

                            # price is at 5th interval
                            elif range_index == 4:
                                # last trade was sell4,sell5,buy5  --> buy6
                                if vol_last_trade_type == 'sell4' or vol_last_trade_type == 'sell5' or vol_last_trade_type == 'buy5':
                                    if checkWeimai(stock) == True:
                                        print(stock, 's')
                                        logging.debug(stock + 's')
                                        buyFunc(stock, last, 'buy6', False)
                        # all intervals close
                        else:
                            volUp2 = getVolUp2(stock)
                            volDown5 = getVolDown5(stock)
                            # above 2nd line，open up interval
                            if last >= volUp2:
                                if checkWeimai(stock) == True:
                                    print(stock, 't')
                                    logging.debug(stock + 't')
                                    sellFunc(stock, last, 'sell2-openUp', position)
                                    print("update 2")
                                    logging.debug("update 2")

                            # below 5th line,open down interval
                            elif last < volDown5:
                                if checkWeimai(stock) == True:
                                    if (last - zhisun_p) / zhisun_p >= 0.02:
                                        print(stock, 'u')
                                        logging.debug(stock + 'u')
                                        buyFunc(stock, last, 'buy5-openDown', False)
                                        print("update 3")
                                        logging.debug("update 3")

                    #write each stock updated info to file, in case exception happened during loop
                    stock_conf.to_csv(stock_config_file, index=False)
                print('DONE this minute')
                logging.debug('DONE this minute')
                w.tlogout(LogonID=1)
                w.stop()

        sleep(5)


if __name__ == '__main__':
    main()
