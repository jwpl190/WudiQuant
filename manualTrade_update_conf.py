# coding=utf-8
# 把中间变量都存到文件中，可随时停止程序

import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import math
import logging

pd.set_option('expand_frame_repr', False)

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


def getVolAbs(stock):
    global stock_conf
    vol_abs = (stock_conf.loc[(stock_conf['Stock'] == stock)])['VolAbs'].values[0]
    return float(vol_abs)


def getBuyLeft(stock):
    global stock_conf
    buy_left = (stock_conf.loc[(stock_conf['Stock'] == stock)])['BuyLeft'].values[0]
    return int(buy_left)


def getSellLeft(stock):
    global stock_conf
    sell_left = (stock_conf.loc[(stock_conf['Stock'] == stock)])['SellLeft'].values[0]
    return int(sell_left)



###############################Load config info from file#####################
def loadConfig():
    global stock_conf
    stock_conf = pd.read_csv(stock_config_file, dtype=str)

###############################Update config info dataframe#####################
def updateConfig(stock, fields, values):
    global stock_conf
    stock_conf.at[stock_conf['Stock'] == stock, fields] = values


##############################Process ready-for-update information############
def process_update(file_name, traded_price):
    stock = file_name.split('_')[0]
    open_trade_type = file_name.split('_')[1]
    if '-' in open_trade_type:  #sell2-openUp, buy5-openDown, sell2-openUpOnly, buy5-openDownOnly
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

    if open_trade_type == 'sell2-openUp':
        vol_abs = getVolAbs(stock)
        updateRangesFromUp(vol_abs, traded_price, stock)
        updateConfig(stock, ["UpOpenFlag"],
                     ['Open'])
    elif open_trade_type == 'buy5-openDown':
        vol_abs = getVolAbs(stock)
        updateRangesFromDown(vol_abs, traded_price, stock)
        updateConfig(stock, ["DownOpenFlag"],
                     ['Open'])
    elif open_trade_type == 'buy5-openDownOnly':
        updateConfig(stock, ["DownOpenFlag"],
                     ['Open'])
    elif open_trade_type == 'sell2-openUpOnly':
        updateConfig(stock, ["UpOpenFlag"],
                     ['Open'])
    updateConfig(stock, ["OpenTradeType"], ["NV"])
    stock_conf.to_csv(stock_config_file, index=False)
#####################initialize variables############################
data_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/manualTrade/"
stock_config_file = data_dir + 'stock_conf_wind_manualTrade.csv'
trade_dir = data_dir + 'trade/'
stock_conf = pd.DataFrame

#########################################Start##########################################################################
def main():
        loadConfig()
        #####################更新#########################################
        file_name = '300124.SZ_sell2-openUp_33.874714576467035_3400_2018-06-26 11-06-10'
        traded_price = 33.95
        ##################################################################
        print ('processing ' + file_name)
        process_update(file_name, traded_price)
        print ('done processing ' + file_name + ', deleting file.')

        file_path = trade_dir + file_name
        os.remove(file_path)

if __name__ == '__main__':
    main()
