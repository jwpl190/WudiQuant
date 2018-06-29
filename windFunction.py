
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
            logging.debug('got position except for stock ' + stock)
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
            TodaySellVolume = int(
                (position_data.loc[(position_data['SecurityCode'] == stock)])['TodaySellVolume'].values[0])
            daily_start_position = getDailyStartPosition(stock)
            sellable = daily_start_position - TodaySellVolume
        except:
            print('got today sell volume except for stock ' + stock)
            logging.debug('got today sell volume except for stock ' + stock)
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


def buyFunc(stock, trade_price, buyType, isDouble):
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


def placeOrder(stock, trade_price, trade_quantity, side, order_type):
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

    updateConfig(stock, ["OpenTradeType", "OpenTradeQuantity", "OpenTradePrice", "OpenTradeId"],
                 [order_type, trade_quantity, trade_price, order_id])
    return 'Success'

def test():
    print ('test')