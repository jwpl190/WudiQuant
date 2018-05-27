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
                    'Zhisun_price': 1.0,
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
                                                'DailyStartPosition'],header='True')



#########################################Start##########################################################################
def main():
    sz50_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/sz50/"
    sz50_config_file = "C:/Users/luigi/Documents/GitHub/WudiQuant/stock_conf_sz50.csv"
    #####Init sz50 config file######
    createConfig(sz50_dir,sz50_config_file)




if __name__ == '__main__':
    main()
