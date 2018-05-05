import tushare as ts
import pandas as pd
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', 500)
from time import sleep
from datetime import datetime, timedelta
from WindPy import *
w.start()

def convertWSDData(data):
    fm = pd.DataFrame(data.Data,index=data.Fields,columns = data.Times)
    fm = fm.T
    return fm
def getStockCode():
    data_dir = "C:/KeLiQuant/"
    stock_codes = pd.read_csv(data_dir + 'ztb.txt', dtype=str)['stock'].values
    return stock_codes

def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes

def calTime(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')

stocks = getStockCode()
# print (len(stocks))
stocks = list(set(stocks))
# print (len(stocks))
for stock in stocks:
    twice = False
    if stock.startswith('6'):
        stock = stock + '.SH'
    elif stock.startswith('0'):
        stock = stock + '.SZ'
    else:
        twice = True
        stock = stock + '.SH'

    print (stock)

    if twice == True:
        data = w.wsd(stock, "WVAD,ROC,RSI,CCI,MTM,TRIX,MACD,SOBV,DMI,ATR,PCT_CHG", "2017-01-01", "2017-03-01",
                 "WVAD_N1=24;WVAD_N2=6;WVAD_IO=1;ROC_interDay=12;ROC_N=6;ROC_IO=1;RSI_N=6;CCI_N=14;"
                 "MTM_interDay=6;MTM_N=6;MTM_IO=1;TRIX_N1=12;TRIX_N2=20;TRIX_IO=1;"
                 "MACD_L=26;MACD_S=12;MACD_N=9;MACD_IO=3;DMI_N=14;DMI_N1=6;DMI_IO=3;ATR_N=14;ATR_IO=2;Fill=Previous;PriceAdj=F")
        data = convertWSDData(data)
        try:
            data.to_csv("C:/KeLiQuant/ztb/" + stock + "_ztb.csv", index=True,
                    columns=["WVAD", "ROC", "RSI", "CCI", "MTM", "TRIX", "MACD", "SOBV", "DMI" , "ATR","PCT_CHG"], header=True)
        except:
            continue
        # print (data)
        stock = stock.replace(".SH",".SZ")
        print (stock)
        data = w.wsd(stock, "WVAD,ROC,RSI,CCI,MTM,TRIX,MACD,SOBV,DMI,ATR,PCT_CHG", "2017-01-01", "2017-03-01",
                 "WVAD_N1=24;WVAD_N2=6;WVAD_IO=1;ROC_interDay=12;ROC_N=6;ROC_IO=1;RSI_N=6;CCI_N=14;"
                 "MTM_interDay=6;MTM_N=6;MTM_IO=1;TRIX_N1=12;TRIX_N2=20;TRIX_IO=1;"
                 "MACD_L=26;MACD_S=12;MACD_N=9;MACD_IO=3;DMI_N=14;DMI_N1=6;DMI_IO=3;ATR_N=14;ATR_IO=2;Fill=Previous;PriceAdj=F")


        data = convertWSDData(data)
        try:
         data.to_csv("C:/KeLiQuant/ztb/" + stock + "_ztb.csv", index=True,
                    columns=["WVAD", "ROC", "RSI", "CCI", "MTM", "TRIX", "MACD", "SOBV", "DMI" , "ATR","PCT_CHG"], header=True)
        except:
            continue
        # print(data)
    else:
        data = w.wsd(stock, "WVAD,ROC,RSI,CCI,MTM,TRIX,MACD,SOBV,DMI,ATR,PCT_CHG", "2017-01-02", "2017-04-01",
                     "WVAD_N1=24;WVAD_N2=6;WVAD_IO=1;ROC_interDay=12;ROC_N=6;ROC_IO=1;RSI_N=6;CCI_N=14;"
                     "MTM_interDay=6;MTM_N=6;MTM_IO=1;TRIX_N1=12;TRIX_N2=20;TRIX_IO=1;"
                     "MACD_L=26;MACD_S=12;MACD_N=9;MACD_IO=3;DMI_N=14;DMI_N1=6;DMI_IO=3;ATR_N=14;ATR_IO=2;Fill=Previous;PriceAdj=F")
        data = convertWSDData(data)
        print (data)
        try:
         data.to_csv("C:/KeLiQuant/ztb/" + stock + "_ztb.csv", mode = 'a',index=True,
                    columns=["WVAD", "ROC", "RSI", "CCI", "MTM", "TRIX", "MACD", "SOBV", "DMI" , "ATR","PCT_CHG"], header=True)
        except:
            continue

