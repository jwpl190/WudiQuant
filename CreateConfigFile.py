# coding=utf-8
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import math
import pickle
import logging
from WindPy import *
logging.basicConfig(filename='windTrade_C003.log', level=logging.DEBUG)

pd.set_option('expand_frame_repr', False)

##create config file based on volatility images##
def createConfig(data_dir,config_file):
    df = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            stock = file.split('-')[0]
            if stock.startswith('6'):
                stock = stock + '.SH'
            else:
                stock = stock + '.SZ'
            rest = file.split('-')[1]
            backday = rest.split(' ')[0]
            d = {
                    'Stock': stock,
                    'BackDays': backday,
                    'Zhisun_day': 60,
                    'Zhisun_price': -1.0,
                    'IsFixZhisunPrice': 'N',
                    'EachStockTradeQuantity': 0,
                    'VolAbs': 0.0,
                    'LastTradeType': 'NV', #default is NV
                    'UpOpenFlag': 'Close', #default is Close
                    'DownOpenFlag': 'Close', #default is Close
                    'ExecTFlag': 'N', #default is N
                    'BuyLeft': 4, #default is 4
                    'SellLeft': 4, #default is 4
                    'VolUp1': 0.0,
                    'VolUp2': 0.0,
                    'VolUp3': 0.0,
                    'VolDown4': 0.0,
                    'VolDown5': 0.0,
                    'VolDown6': 0.0,
                    'SpecialZhisunFlag': 'N', #default is N
                    'SpecialZhisunPrice': 0.0,
                    'SpecialZhisunDay': 0,
                    'OpenTradeType': 'NV', #default is NV
                    'OpenTradeQuantity': 0,
                    'OpenTradePrice': 0.0,
                    'OpenTradeId': '0',
                    'ZhisunFlag': 'N',#default is N
                    'DailyStartPosition': 0
                }
            df.append(d)
            print (stock)
            print (backday)
    df = pd.DataFrame(df)
    df.to_csv(config_file, index=False,columns=['Stock','BackDays','Zhisun_day','Zhisun_price','IsFixZhisunPrice',
                                                'EachStockTradeQuantity','VolAbs','LastTradeType','UpOpenFlag','DownOpenFlag',
                                                'ExecTFlag','BuyLeft','SellLeft','VolUp1','VolUp2','VolUp3','VolDown4',
                                                'VolDown5','VolDown6','SpecialZhisunFlag','SpecialZhisunPrice','SpecialZhisunDay',
                                                'OpenTradeType','OpenTradeQuantity','OpenTradePrice','OpenTradeId','ZhisunFlag',
                                                'DailyStartPosition'],header=True)

####################################################################
def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes

def conWSDData(data):
    fm = pd.DataFrame(data.Data, index=data.Fields, columns=data.Times)
    fm = fm.T  # Transpose index and columns
    return fm
#############################################################################
def getMSCIweight(image_dir,msci_dir):
    curTime = datetime.today().strftime('%H-%M-%S')
    curTime = '2018-06-01'
    stocks = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            stock = file.split('-')[0]
            if stock.startswith('6'):
                stock = stock + '.SH'
            else:
                stock = stock + '.SZ'
            stocks.append(stock)
    parsedStock = parseStock(stocks)
    stock_mktCap = {}
    ttl_mktCap = 0.0
    w.start()
    data = w.wsd(parsedStock, "mkt_cap_ard", curTime, curTime, "unit=1;Currency=CNY;PriceAdj=F")
    for i in range(0,len(data.Codes)):
        stock = data.Codes[i]
        mkt_cap = float(data.Data[0][i])
        stock_mktCap[stock] = mkt_cap
        ttl_mktCap = ttl_mktCap + mkt_cap
    df = []
    for stock in stock_mktCap.keys():
        weight = stock_mktCap[stock] / ttl_mktCap *100
        d = {
                'Stock': stock,
                'Weight': weight
        }
        df.append(d)
    df = pd.DataFrame(df)
    df.to_csv(msci_dir + 'msci_weight.csv', index=False, columns=['Stock','Weight'],header='True')

#########################################Start##########################################################################
def main():
    # sz50_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/sz50/"
    # sz50_config_file = "C:/Users/luigi/Documents/GitHub/WudiQuant/stock_conf_sz50.csv"
    # #####Init sz50 config file######
    # createConfig(sz50_dir,sz50_config_file)

    msci_dir = 'C:/KeLiQuant/msci/'
    msci_images = msci_dir + 'msci_image/'
    msci_config_file = 'C:/Users/luigi/Documents/GitHub/WudiQuant/stock_conf_msci.csv'
    # getMSCIweight(msci_images,msci_dir)
    createConfig(msci_images,msci_config_file)



if __name__ == '__main__':
    main()
