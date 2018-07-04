# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。

import pandas as pd
from WindPy import *
from time import sleep
# 股价低于学习到的MA5，1-2个点就进场
# 涨到学习到的MA5（或加一个波动率）就出场
# 止损在10日均线
# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
###########################round to 100################
def truncate(f, n):
    '''Truncates/pads a int f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d + '0' * n)[:n]])


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


###########################Parse stock list for Wind query#####################
def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes


def getStockPositionWind(position_data, stock):
    if 'SecurityCode' not in position_data.columns:
        return -999
    stocks = list(position_data['SecurityCode'].values)
    if stock in stocks:
        try:
            position = int((position_data.loc[(position_data['SecurityCode'] == stock)])['SecurityVolume'].values[0])
        except:
            print('got position except for stock ' + stock)

            return -999
    else:
        position = -999
    return position


def getStockSellable(position_data, stock):
    if 'SecurityCode' not in position_data.columns:
        return 0
    stocks = list(position_data['SecurityCode'].values)
    if stock in stocks:
        try:

            sellable = int(
                (position_data.loc[(position_data['SecurityCode'] == stock)])['SecurityAvail'].values[0])

        except:
            print('got today sell volume except for stock ' + stock)

            return 0
    else:
        sellable = 0
    return sellable


##############################buy function######################
def tradeFunc_ma5(stock, order_price, order_quantity, isDouble, side):
    if isDouble == True:
        order_quantity = order_quantity * 2
    order_quantity = int(float(truncate(order_quantity / 100, 0)) * 100)

    if side == 'buy':
        status = placeOrder_ma5(stock, order_price, order_quantity, "Buy")
    else:
        status = placeOrder_ma5(stock, order_price, order_quantity, "Sell")
    if status == 'Success':
        print(stock, ' success place ' + side + ' order')
    elif status == 'Failed':
        print(stock, ' failed place ' + side + ' order')




##############################Place an order##############################
def placeOrder_ma5(stock, trade_price, trade_quantity, side):
    order_data = conWSDData(w.torder(stock, side, trade_price, trade_quantity, "OrderType=LMT;LogonID=1"))
    if 'RequestID' not in order_data.columns:
        print('request id is not in order data, place order failed')
        return 'Failed'
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

    return 'Success'



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
data_dir = "Z:/Documents/GitHub/WudiQuant/"
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
            global stock_conf, stocks, zhisun_stock, zhisun_stock_temp, jinchang, ma5_price, price_zhisun, exit_price, stock_exec_flag
            ###########################################################trading#####################################################################
            if curTime == '09-25':
                for stock in stocks.keys():
                    stock_exec_flag[stock] = True

            if curTime == '12-55':
                stock_conf = pd.read_csv(config_file, dtype=str)
                zhisun_stock = []
                zhisun_stock_temp = []
                jinchang = []
                ma5_price = {}
                price_zhisun = {}
                exit_price = {}
                stock_exec_flag = {}
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

                w.tlogon("0000", "0", "W104343300531", "********", "SHSZ")
                try:
                    curAllStockPosition = conWSQData(w.tquery('Position', 'LogonID=1'))

                except:
                    print('got current stock position except')

                    w.tlogout(LogonID=1)
                    w.stop()
                    sleep(2)
                    continue

                parsedStock = parseStock(stocks)
                try:
                    last_price_data = w.wsq(parsedStock, 'rt_last')
                except:
                    print('got current stocks price excep')
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

                    position = getStockPositionWind(curAllStockPosition, stock)
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
                                    tradeFunc_ma5(stock, order_price, order_quantity, False,'buy')
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
                                tradeFunc_ma5(stock, order_price, sellable, False, 'sell')
                                stock_exec_flag[stock] == False
                                if stock not in zhisun_stock_temp:
                                    zhisun_stock_temp.append(stock)
                                continue
                            # 止损
                            if last < price_zhisun[stock] or stock in zhisun_stock_temp:
                                print('zhisun ', stock)
                                sellable = getStockSellable(curAllStockPosition, stock)
                                order_price = last * 0.998
                                tradeFunc_ma5(stock, order_price, sellable, False, 'sell')
                                stock_exec_flag[stock] == False
                                if stock not in zhisun_stock_temp:
                                    zhisun_stock_temp.append(stock)
                                continue
                            # 出场
                            if last >= exit_price[stock]:
                                print('chu chang ', stock)
                                sellable = getStockSellable(curAllStockPosition, stock)
                                order_price = last * 0.998
                                tradeFunc_ma5(stock, order_price, sellable, False, 'sell')
                                stock_exec_flag[stock] == False
                                if stock not in zhisun_stock_temp:
                                    zhisun_stock_temp.append(stock)
                                continue

                stocks = updateAllStocks()
        sleep(5)






