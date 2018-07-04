#-*-coding:utf-8-*-
from WindPy import *
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import math
import pickle
import logging
# import sys
#
# reload(sys)
#
# sys.setdefaultencoding('gbk')

pd.set_option('expand_frame_repr', False)
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
###########################round to 100################
def truncate(f, n):
    '''Truncates/pads a int f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d + '0' * n)[:n]])


def getOpenTradeType(stock):
    global stock_conf
    open_trade_type = (stock_conf.loc[(stock_conf['Stock'] == stock)])['OpenTradeType'].values[0]
    return str(open_trade_type)
###########################Parse stock list for Wind query#####################
def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes


##############################buy first trade function######################
def buyFirstFunc(stock, last,buy_cash):
    trade_price = last * 1.002
    order_quantity = buy_cash / trade_price
    if order_quantity < 400:
        order_quantity = 400
    order_quantity = int(float(truncate(order_quantity / 100, 0)) * 100)

    order_id = placeOrder(stock, trade_price, order_quantity, "Buy", "FirstTime")
    if order_id == 'Failed':
        print(stock, ' failed place order first time')
        # logging.debug(stock + ' failed place order first time')
        return 'Not OK'
    else:
        print (stock, ' success place order first time')
        sleep(5)
        ###check if order executed successfully###########################
        query_data = conWSDData(w.tquery('Order', 'LogonID=1;OrderNumber=' + order_id))
        # order_volume = int(query_data['OrderVolume'].values[0])
        traded_volume = int(query_data['TradedVolume'].values[0])

        if traded_volume != order_quantity:
            # remark = str(query_data['Remark'].values[0])
            print (query_data)
            remark = query_data['Remark'].values[0]
            print('成交量与下单量不符: order_number: ' +  order_id)
            print(remark)
            if remark == u'已报':
                print('废单')
            return 'Not OK'
        else:
            each_trade_quantity = traded_volume / 4
            each_trade_quantity = int(float(truncate(each_trade_quantity / 100, 0)) * 100)
            updateConfig(stock, ["EachStockTradeQuantity"], [each_trade_quantity])
            stock_conf.to_csv(stock_config_file, index=False)
            return 'OK'


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
    return order_id


###############################Load config info from file#####################
def loadConfig(stock_config_file):
    global stock_conf
    stock_conf = pd.read_csv(stock_config_file, dtype=str)

###############################Update config info dataframe#####################
def updateConfig(stock, fields, values):
    global stock_conf
    stock_conf.at[stock_conf['Stock'] == stock, fields] = values

###################Get weight from file#########################
def getWeight(file):
    weight_data = pd.read_csv(file,dtype=str)
    return weight_data


###################Get stock list from file#########################
def getStocks(file):

    data = pd.read_csv(file,dtype=str)
    stocks = list(data['Stock'].values)
    return stocks

##################Buy MSCI first time #############################
def buyMSCIFirstTime(file_dir):
    weight_data = getWeight(file_dir)
    stocks = list(weight_data['Stock'].values)
    parsedStock = parseStock(stocks)
    try:
        last_price_data = w.wsq(parsedStock, 'rt_last')
    except:
        print('got MSCI current stocks price excep')
    # print (last_price_data)
    # num_stock = len(last_price_data.Codes)
    # if num_stock != 50:
    #     print ('got number of stocks price: ' + num_stock)
    #     print ('not right, exit')
    #     return
    for i in range(0, len(last_price_data.Codes)):
        stock = last_price_data.Codes[i]
        last = last_price_data.Data[0][i]
        if last <0:
            continue
        weight = float((weight_data.loc[(weight_data['Stock'] == stock)])['Weight'].values[0])
        cash = 10000000 * 0.8
        buy_cash = cash * (weight / 100)  # cash to buy
        res = buyFirstFunc(stock,last,buy_cash)
        if res == 'Not OK':
            print (stock, ' did not buy first time')
        elif res == 'OK':
            print(stock, ' success buy first time')

###################Buy SZ50 first time #############################
def buySZ50FirstTime(file_dir):
    weight_data = getWeight(file_dir)
    stocks = list(weight_data['Stock'].values)
    parsedStock = parseStock(stocks)
    try:
        last_price_data = w.wsq(parsedStock, 'rt_last')
    except:
        print('got SZ50 current stocks price excep')
    # num_stock = len(last_price_data.Codes)
    # if num_stock != 50:
    #     print ('got number of stocks price: ' + num_stock)
    #     print ('not right, exit')
    #     return
    for i in range(0, len(last_price_data.Codes)):
        stock = last_price_data.Codes[i]
        last = last_price_data.Data[0][i]
        if last <1:
            continue
        weight = float((weight_data.loc[(weight_data['Stock'] == stock)])['Weight'].values[0])
        cash = 10000000 * 0.8
        buy_cash = cash * (weight / 100)  # cash to buy
        res = buyFirstFunc(stock,last,buy_cash)
        if res == 'Not OK':
            print (stock, ' did not buy first time')
        elif res == 'OK':
            print(stock, ' success buy first time')

###################Buy stock first time #############################
def buyStocksFirstTime():
    global stock_conf
    stocks = list(stock_conf['Stock'].values)
    parsedStock = parseStock(stocks)
    try:
        last_price_data = w.wsq(parsedStock, 'rt_last')
    except:
        print('got current stocks price excep')
    for i in range(0, len(last_price_data.Codes)):
        stock = last_price_data.Codes[i]
        last = last_price_data.Data[0][i]
        buy_cash = 10000000 * 0.8 / 10
        # buy_cash = 3800000/8
        res = buyFirstFunc(stock, last, buy_cash)
        if res == 'Not OK':
            print(stock, ' did not buy first time')
        elif res == 'OK':
            print(stock, ' success buy first time')


def buyC003():
    w.tlogon("0000", "0", "W124041900431", "********", "SHSZ")
    #place order##
    buyStocksFirstTime()
    w.tlogout(LogonID=1)

def buySZ50():
    w.tlogon("0000", "0", "W124041900401", "********", "SHSZ")
    sz50_weight_file = data_dir + 'sz50_weight.csv'
    #place order##
    buySZ50FirstTime(sz50_weight_file)
    w.tlogout(LogonID=1)

def buyMSCI():
    w.tlogon("0000", "0", "W104343300501", "********", "SHSZ")
    msci_weight_file = data_dir + 'msci_weight.csv'
    # place order##
    buyMSCIFirstTime(msci_weight_file)
    w.tlogout(LogonID=1)

#####################initialize variables############################


# data_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/"
data_dir = "Z:/Documents/GitHub/WudiQuant/"
stock_conf = pd.DataFrame
# stock_config_file = data_dir + 'stock_conf_sz50.csv'
# stock_config_file = data_dir + 'stock_conf_wind_test_C003_buyfirst.csv'
stock_config_file = data_dir + 'stock_conf_msci.csv'

#########################################Start##########################################################################
def main():
    ##load config from config file##
    loadConfig(stock_config_file)

    w.start()

    # buyC003()
    # buySZ50()
    buyMSCI()

    w.stop()


if __name__ == '__main__':
    main()
