from WindPy import *
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import math
import requests
from pathlib import Path

pd.set_option('expand_frame_repr', False)

def calTime1(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')






def getAllStock():
    allStock = w.wset("sectorconstituent", "sectorid=a001010100000000;field=wind_code")
    fm = pd.DataFrame(allStock.Data, index=allStock.Fields)
    fm = fm.T  # Transpose index and columns
    code_list = fm['wind_code'].values
    return code_list
    # return parseStock(code_list)
def parseStock(code_list):
    codes = ''
    ct = 1
    for code in code_list:
        if ct<=900:
            codes += code
            codes += ','
            ct = ct+1
    codes = codes[:len(codes) - 1]
    return codes

def conWSQData(indata1):
    fm = pd.DataFrame(indata1.Data, index=indata1.Fields, columns=indata1.Codes)
    fm = fm.T  # Transpose index and columns
    # fm['code'] = fm.index
    fm['datetime'] = indata1.Times[0]
    return fm

def calTime(original_datetime, delta):

    return (datetime.strptime(original_datetime, '%Y-%m-%d %H-%M-%S') + timedelta(hours=delta)).strftime('%Y-%m-%d %H-%M-%S')

def conWSETData(indata1):
    fm = pd.DataFrame(indata1.Data, index=indata1.Fields, columns=indata1.Times)
    fm = fm.T  # Transpose index and columns
    return fm

w.start()
codeList = getAllStock()
print (len(codeList))
w.stop()
codeLists = []

eachListLength = 100
for i in range(0,len(codeList),eachListLength):
    if i+eachListLength > len(codeList):
        codeLists.append(codeList[i:])
    else:
        codeLists.append(codeList[i:i+eachListLength])

data_dir = 'C:\KeLiQuant\WindRTData\\'
while (1):
    weekno = datetime.today().weekday()
    if weekno in [0,1,2,3,4]:
        curTime = datetime.today().strftime('%H-%M-%S')
        if(curTime >= '09-30-00' and curTime <= '11-30-59') or (curTime >= '13-00-00' and curTime <= '15-00-59'):
            w.start()
            for code_list in codeLists:
                parsedStocks = parseStock(code_list)
                try:
                    data = conWSQData(w.wsq(parsedStocks,'rt_insti_inflow,rt_vip_inflow,rt_mid_inflow,rt_indi_inflow,rt_bidvol,rt_askvol,'
                                              'rt_bsize_total ,rt_asize_total,rt_insti_activebuy_amt,rt_vip_activebuy_amt,rt_mid_activebuy_amt,'
                                              'rt_indi_activebuy_amt,rt_insti_activesell_amt,rt_vip_activesell_amt,rt_mid_activesell_amt,rt_indi_activesell_amt,rt_last,rt_downward_vol,rt_upward_vol'))
                except:
                    print ('except 1')
                    continue
                for row in data.itertuples():
                    stock = row[0]
                    file_name = data_dir + stock + '_rtdata'
                    if not Path(file_name).is_file():
                        header = 'rt_insti_inflow,rt_vip_inflow,rt_mid_inflow,rt_indi_inflow,rt_bidvol,rt_askvol,' \
                                 'rt_bsize_total ,rt_asize_total,rt_insti_activebuy_amt,rt_vip_activebuy_amt,rt_mid_activebuy_amt,' \
                                 'rt_indi_activebuy_amt,rt_insti_activesell_amt,rt_vip_activesell_amt,rt_mid_activesell_amt,rt_indi_activesell_amt,rt_last,rt_downward_vol,rt_upward_vol,datetime'
                        fd = open(file_name, 'a')
                        fd.write(header)
                        fd.write('\n')
                        fd.close()
                    df =  pd.DataFrame(list(row[1:]))
                    df = df.T  # Transpose index and columns
                    df.to_csv(file_name,index=False,header=False,mode='a')
            w.stop()
            print ('done this minute')


    sleep(50)



