import pandas as pd

###########################round to 100################
def truncate(f, n):
    '''Truncates/pads a int f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d + '0' * n)[:n]])




trade_file = '/Users/keli/Documents/Quant/trade.csv'
stock_config_file = '/Users/keli/Documents/GitHub/WudiQuant/stock_conf_msci.csv'
trade_data = pd.read_csv(trade_file, dtype=str)
stock_conf = pd.read_csv(stock_config_file, dtype=str)

for row in trade_data.itertuples():
    stock =  row[1]
    volume = int(row[2])
    volume  = int(float(truncate(volume/4 / 100, 0)) * 100)
    print (stock)
    print (volume)
    stock_conf.at[stock_conf['Stock'] == stock, 'EachStockTradeQuantity'] = volume

stock_conf.to_csv(stock_config_file, index=False)

exit(0)

