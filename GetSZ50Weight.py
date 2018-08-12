from WindPy import *
import pandas as pd

def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes

data_dir = "C:/Users/luigi/Documents/GitHub/WudiQuant/"
stock_codes = pd.read_csv(data_dir + 'sz50_weight.csv',dtype=str)['Stock'].values
parsed_stock_codes = parseStock(stock_codes)

w.start()
volume_data = w.wsd(parsed_stock_codes, "amt", "2018-08-10", "2018-08-12", "")
ttl_volume = 0
stock_volume = {}
for i in range(0, len(volume_data.Codes)):
    stock = volume_data.Codes[i]
    volume = volume_data.Data[0][i]
    print (stock)
    print (volume)
    stock_volume[stock] = volume
    ttl_volume = ttl_volume + volume

filename = data_dir + 'sz50_weight_v2.csv'
fd = open(filename, 'a')
for stock in stock_volume:
    weight = stock_volume[stock]/ttl_volume * 100
    row = stock + ',' + str(weight)

    fd.write(row)
    fd.write('\n')
fd.close()
