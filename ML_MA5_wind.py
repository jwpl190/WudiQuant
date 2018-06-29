# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import math
import tushare as ts
from datetime import datetime, timedelta
import numpy as np
import talib
import sys
import pandas as pd
from six import BytesIO
import csv
import windFunction as wind

# 股价低于学习到的MA5，1-2个点就进场
# 涨到学习到的MA5（或加一个波动率）就出场
# 止损在10日均线
# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。

def getMA5(stock):
    global stock_conf
    ma5 = (stock_conf.loc[(stock_conf['Stock'] == stock)])['MA5'].values[0]
    return ma5


def updateAllStocks():
    for stock in zhisun_stock:
        if stock in stocks:
            stocks.remove(stock)
            zhisun_stock_temp.remove(stock)
    return stocks


# 删除止损过的股票，如果需要让止损股票重新进场，BackFlag设置为Y
def getAllStocks():
    global stock_conf
    orig_stocks = stock_conf['Stock'].values
    ret_stock = []
    for stock in orig_stocks:
        if stock not in zhisun_stock:
            ret_stock.append(stock)
    for stock in ret_stock:
        if stock in zhisun_stock:
            zhisun_stock.remove(stock)
        if stock in zhisun_stock_temp:
            zhisun_stock_temp.remove(stock)
    return ret_stock

def calTime(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')


############################################################################
data_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/"
config_file = data_dir + 'stock_ma5_conf.txt'
zhisun_stock = []
zhisun_stock_temp = []
each_stock_cash = {}
price_zhisun = {}
ma5_price = {}
exit_price = {}
jinchang = []
stock_exec_flag = {}

number_of_stocks = 5
stock_conf = pd.DataFrame
stocks = []


#########################################Start##########################################################################
def main():
    while 1:
        weekno = datetime.today().weekday()
        if weekno in [0, 1, 2, 3, 4]:  # should be [0,1,2,3,4]
            date_time = datetime.today().strftime('%Y-%m-%d %H-%M')
            curTime = date_time.split(' ')[1]
            global stock_conf, stocks,zhisun_stock,zhisun_stock_temp,jinchang
            ###########################################################trading#####################################################################
            if curTime == '09-25':
                for stock in stocks.keys():
                    stock_exec_flag[stock] = True

            if curTime == '12-55':
                stock_conf = pd.read_csv(config_file, dtype=str)
                zhisun_stock = []
                zhisun_stock_temp = []
                jinchang = []
                stocks = getAllStocks()
                print('number of stocks: ', str(len(stocks)))
                for stock in stocks:
                    ma5_price[stock] = getMA5(stock)
                    price_zhisun[stock] = 0
                    exit_price[stock] = 0
                    stock_exec_flag[stock] = True

            if (curTime >= '09-30' and curTime <= '11-30') or (curTime >= '13-00' and curTime <= '15-00'):
                w.start()
                print('START this minute ', date_time)
                logging.debug('START this minute ' + date_time)
                w.tlogon("0000", "0", "W124041900401", "********", "SHSZ")
                try:
                    curAllStockPosition = wind.conWSQData(w.tquery('Position', 'LogonID=1'))

                except:
                    print('got current stock position except')
                    logging.debug('got current stock position except')
                    w.tlogout(LogonID=1)
                    w.stop()
                    sleep(2)
                    continue

                parsedStock = wind.parseStock(stocks)
                try:
                    last_price_data = w.wsq(parsedStock, 'rt_last')
                except:
                    print('got current stocks price excep')
                    logging.debug('got current stocks price excep')
                    w.tlogout(LogonID=1)
                    w.stop()
                    sleep(2)
                    continue
                for i in range(0, len(last_price_data.Codes)):
                    stock = last_price_data.Codes[i]
                    last = last_price_data.Data[0][i]

                    order_data = conWSDData(w.tquery('Order', 'LogonID=1;Windcode=' + stock))
                    if 'SecurityCode' in order_data.columns:
                        print ('has existing order for stock ', stock)
                        continue

                    position = wind.getStockPositionWind(curAllStockPosition, stock)
                    if position == -999:
                        print('get stock position except')
                        continue
                    if position == 0:

                        # 如果出现止损，丢掉该股票
                        if stock in zhisun_stock_temp:
                            if stock not in zhisun_stock:
                                zhisun_stock.append(stock)
                            continue
                        ma5 = ma5_price[stock]
                        print(ma5)
                        if last <= ma5 * 0.95:
                            if stock not in jinchang:
                                if len(jinchang) < number_of_stocks:
                                    print(stock)
                                    print("jin chang")
                                    jinchang.append(stock)
                                    buy_cash = each_stock_cash[stock]
                                    order_price = last * 1.002
                                    order_quantity = buy_cash/order_price
                                    wind.tradeFunc_ma5(stock, order_price, order_quantity, False,'buy')
                                    exit_price[stock] = ma5
                                    price_zhisun[stock] = last * 0.98
                                    stock_exec_flag[stock] = False

                    else:
                        if stock_exec_flag[stock] == True:
                            # time's up
                            if curTime == '11-20':
                                print('times up ', stock)
                                sellable = getStockSellable(curAllStockPosition, stock)
                                order_price = last * 0.998
                                wind.tradeFunc_ma5(stock, order_price, sellable, False, 'sell')
                                if stock not in zhisun_stock_temp:
                                    zhisun_stock_temp.append(stock)
                                continue
                            # 止损
                            if last < price_zhisun[stock] or stock in zhisun_stock_temp:
                                print('zhisun ', stock)
                                sellable = getStockSellable(curAllStockPosition, stock)
                                order_price = last * 0.998
                                wind.tradeFunc_ma5(stock, order_price, sellable, False, 'sell')
                                if stock not in zhisun_stock_temp:
                                    zhisun_stock_temp.append(stock)
                                continue
                            # 出场
                            if last >= exit_price[stock]:
                                print('chu chang ', stock)
                                sellable = getStockSellable(curAllStockPosition, stock)
                                order_price = last * 0.998
                                wind.tradeFunc_ma5(stock, order_price, sellable, False, 'sell')
                                if stock not in zhisun_stock_temp:
                                    zhisun_stock_temp.append(stock)
                                continue

                stocks = updateAllStocks()







