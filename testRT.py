from WindPy import *
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import mysql.connector

w.start()
pd.set_option('expand_frame_repr', False)

# today = '2018-01-04'
# data = w.wset("shhktransactionstatistics","startdate=" + today + ";enddate=" + today + ";cycle=day;currency=cny;field=sh_net_purchases,hk_net_purchases")
#
# print (data)
# exit(0)
def calTime(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')


def conWSQData(indata1):

    fm = pd.DataFrame(indata1.Data, index=indata1.Fields, columns=indata1.Codes)
    fm = fm.T  # Transpose index and columns
    fm['code'] = fm.index
    fm['datetime'] = indata1.Times[0]
    print (fm)


# data = w.wsq("000063.SZ", "rt_vol", func=conWSQData)
data = w.wsq("000063.SZ", "rt_amt", func=conWSQData)

while (1):
    info = 'a'



