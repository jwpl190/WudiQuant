from WindPy import *
import pandas as pd
from time import sleep
# w.start()

pd.set_option('expand_frame_repr', False)

def calTime1(original_datetime, delta):
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

def calTime(original_datetime, delta):

    return (datetime.strptime(original_datetime, '%H-%M') + timedelta(hours=delta)).strftime('%H-%M')

def conWSETData(indata1):
    fm = pd.DataFrame(indata1.Data, index=indata1.Fields, columns=indata1.Times)
    fm = fm.T  # Transpose index and columns
    return fm

data_dir = "C:/KeLiQuant/"
stock_codes = pd.read_csv(data_dir + 'MA5_stock',dtype=str)['stock'].values
parsed_stock_codes = parseStock(stock_codes)



while (1):
    weekno = datetime.today().weekday()
    if weekno in [0,1,2,3,4]:
        curTime = datetime.today().strftime('%H-%M')
        if curTime == '11-35':
            #Get stock ma5
            w.start()
            try:
                data = conWSQData(w.wsq(parsed_stock_codes,'rt_ma_5d'))
                data.to_csv("C:/KeLiQuant/ma5_res",index = False,columns=['code','RT_MA_5D'])
                print ('done')

            except:
                print ('except')
            w.stop()
            #Get index ma5


    sleep(60)



