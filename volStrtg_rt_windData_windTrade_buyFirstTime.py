# coding=utf-8
# 把中间变量都存到文件中，可随时停止程序
# from WindPy import *
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



###########################Parse stock list for Wind query#####################
def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes


##############################buy first trade function######################
def buyFirstFunc(stock, last,weightData):
    weight = (weightData.loc[(weightData['Stock'] == stock)])['Weight'].values[0]
    global cash
    buy_cash = cash * (weight/100)  # cash to buy
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
        sleep(3)
        query_data = conWSDData(w.tquery('Order', 'LogonID=1;OrderNumber=' + order_id))
        # order_volume = int(query_data['OrderVolume'].values[0])
        traded_volume = int(query_data['TradedVolume'].values[0])

        if traded_volume != order_quantity:
            remark = str(query_data['Remark'].values[0])
            print('成交量与下单量不符合！order number: ', order_id)
            print('remark: ', remark)
            if remark == '废单':
                print(stock + ' 废单')
            return 'Not OK'


        else:
            each_trade_quantity = traded_volume / 4
            each_trade_quantity = int(float(truncate(each_trade_quantity / 100, 0)) * 100)
            updateConfig(stock, ["EachStockTradeQuantity"], [each_trade_quantity])
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
def loadConfig():
    global stock_conf
    stock_conf = pd.read_csv(stock_config_file, dtype=str)

###############################Update config info dataframe#####################
def updateConfig(stock, fields, values):
    global stock_conf
    stock_conf.at[stock_conf['Stock'] == stock, fields] = values

###################Get weight from file#########################
def getSZ50Weight(dir):
    sz50_file = dir + "sz50_weight.csv"
    weight_data = pd.read_csv(sz50_file,dtype=str)
    return weight_data

###################Buy SZ50 first time #############################
def buySZ50FirstTime():
    weight_data = getSZ50Weight(data_dir)
    stocks = list(weight_data['Stock'].values)
    parsedStock = parseStock(stocks)
    try:
        last_price_data = w.wsq(parsedStock, 'rt_last')
    except:
        print('got SZ50 current stocks price excep')
    num_stock = len(last_price_data.Codes)
    if num_stock != 50:
        print ('got number of stocks price: ' + num_stock)
        print ('not right, exit')
        return
    for i in range(0, len(last_price_data.Codes)):
        stock = last_price_data.Codes[i]
        last = last_price_data.Data[0][i]
        res = buyFirstFunc(stock,last,weight_data)
        if res == 'Not OK':
            print (stock, ' did not buy first time')
        elif res == 'OK':
            print(stock, ' success buy first time')


#####################initialize variables############################
# data_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/"
data_dir = "/Users/keli/Documents/Quant/"
stock_config_file = data_dir + 'stock_conf_wind_sz50.csv'
cash = 10000000
stock_conf = pd.DataFrame



#########################################Start##########################################################################
def main():
    loadConfig()
    buySZ50FirstTime()


if __name__ == '__main__':
    main()
