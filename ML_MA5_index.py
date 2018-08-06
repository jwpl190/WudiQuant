from WindPy import *
import pandas as pd
from time import sleep
import numpy as np
import talib
# w.start()
import tushare as ts

pd.set_option('expand_frame_repr', False)


def calTimeDate(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')


def parseStock(code_list):
    codes = ''
    for code in code_list:
        codes += code
        codes += ','
    codes = codes[:len(codes) - 1]
    return codes


def conWSQData(indata1):
    fm = pd.DataFrame(indata1.Data, index=indata1.Fields, columns=indata1.Codes)
    fm = fm.T  # Transpose index and columns
    fm['code'] = fm.index
    fm['datetime'] = indata1.Times[0]
    return fm


data_dir = "Z:/Documents/GitHub/WudiQuant/"
stock_codes = pd.read_csv(data_dir + 'MA5_stock', dtype=str)['stock'].values
parsed_stock_codes = parseStock(stock_codes)

index_code = ['000001.SH', '399001.SZ', '399006.SZ']
wind_tushare_index_map = {}
wind_tushare_index_map['000001.SH'] = []
wind_tushare_index_map['399001.SZ'] = []
wind_tushare_index_map['399006.SZ'] = []

while (1):
    weekno = datetime.today().weekday()
    if weekno in [0, 1, 2, 3, 4]:
        dateTime = datetime.today().strftime('%Y-%m-%d %H-%M')
        curDate = dateTime.split(' ')[0]
        curTime = dateTime.split(' ')[1]
        if curTime == '11-32':
            startDay = calTimeDate(curDate, -180)

            df = ts.get_hist_data('sh', start=startDay, end=curDate, retry_count=10, pause=2)
            df.sort_index(inplace=True)
            wind_tushare_index_map['000001.SH'] = list(df['close'].values)

            df = ts.get_hist_data('sz', start=startDay, end=curDate, retry_count=10, pause=2)
            df.sort_index(inplace=True)
            wind_tushare_index_map['399001.SZ'] = list(df['close'].values)

            df = ts.get_hist_data('cyb', start=startDay, end=curDate, retry_count=10, pause=2)
            df.sort_index(inplace=True)
            wind_tushare_index_map['399006.SZ'] = list(df['close'].values)

            # Get stock ma5
            w.start()

            for index in index_code:
                wdata = w.wsq(index, 'rt_last')
                last = wdata.Data[0][0]
                wind_tushare_index_map[index].append(last)

            outDf = []
            for index in wind_tushare_index_map.keys():
                ma5 = talib.SMA(np.asarray(wind_tushare_index_map[index]), 5)[-1]
                d = {'code': index,
                     'RT_MA_5D': ma5}
                outDf.append(d)
            outDf = pd.DataFrame(outDf)
            outDf.to_csv("Z:/Documents/GitHub/WudiQuant/ma5_res", index=False, columns=['code', 'RT_MA_5D'])

            try:
                data = conWSQData(w.wsq(parsed_stock_codes, 'rt_ma_5d'))
                data.to_csv("Z:/Documents/GitHub/WudiQuant/ma5_res", index=False, columns=['code', 'RT_MA_5D'], header=False, mode='a')

            except:
                print('except')

            w.stop()

            print('done')

    sleep(60)
