import tushare as ts
import pandas as pd
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', 500)
from time import sleep
from datetime import datetime, timedelta

stocks = []
stocks.append('002714')
stocks.append('000830')
stocks.append('000425')
stocks.append('600340')
stocks.append('001979')
stocks.append('600787')
stocks.append('000581')
stocks.append('601002')
stocks.append('600104')
stocks.append('000063')
stocks.append('000801')
stocks.append('600699')
stocks.append('600297')
stocks.append('300496')
stocks.append('603019')
stocks.append('601766')
stocks.append('600507')
stocks.append('000877')
stocks.append('002151')
stocks.append('002185')

def calTime(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')


while(1):
    weekno = datetime.today().weekday()
    if weekno in [0, 1, 2, 3, 6]:
        curTime = datetime.today().strftime('%H-%M-%S')
        today = datetime.today().strftime('%Y-%m-%d')
        today = calTime(today, +1)
        if (curTime >= '17-30-00' and curTime <= '19-30-59') or (curTime >= '21-00-00' and curTime <= '23-00-59'):
                    for stock in stocks:
                        try:
                            data = ts.get_realtime_quotes(stock)
                        except:
                            continue
                        data.to_csv("C:/KeLiQuant/Weimai_tushare/" + stock + "_"+today+".csv",index=False,columns=["code", "b1_v","b2_v","b3_v","b4_v","b5_v","a1_v","a2_v","a3_v"
                            ,"a4_v","a5_v","time"],mode='a',header = False)
    sleep(45)