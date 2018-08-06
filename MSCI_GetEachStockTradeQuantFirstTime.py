import pandas as pd

###########################round to 100################
def truncate(f, n):
    '''Truncates/pads a int f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d + '0' * n)[:n]])


def updateEachStockTradeQuantity():

    trade_file = '/Users/keli/Documents/Quant/trade.csv'
    stock_config_file = '/Users/keli/Documents/GitHub/WudiQuant/stock_conf_msci.csv'
    trade_data = pd.read_csv(trade_file, dtype=str)
    stock_conf = pd.read_csv(stock_config_file, dtype=str)

    for row in trade_data.itertuples():
        stock =  row[1]
        if stock.startswith('6'):
            stock = stock + '.SH'
        else:
            stock = stock + '.SZ'
        volume = int(row[2])
        volume  = int(float(truncate(volume/4 / 100, 0)) * 100)
        print (stock)
        print (volume)
        stock_conf.at[stock_conf['Stock'] == stock, 'EachStockTradeQuantity'] = volume

    stock_conf.to_csv(stock_config_file, index=False)

def updateExcecuteFlag():
    untrade_file = '/Users/keli/Documents/Quant/untrade.csv'
    stock_config_file = '/Users/keli/Documents/GitHub/WudiQuant/stock_conf_msci.csv'
    untrade_data = pd.read_csv(untrade_file, dtype=str)
    stock_conf = pd.read_csv(stock_config_file, dtype=str)

    for row in untrade_data.itertuples():
        stock = row[1]
        if stock.startswith('6'):
            stock = stock + '.SH'
        else:
            stock = stock + '.SZ'

        stock_conf.at[stock_conf['Stock'] == stock, 'ExecTFlag'] = 'N'

def main():
    updateEachStockTradeQuantity()
    # updateExcecuteFlag()

if __name__ == '__main__':
    main()


