from WindPy import *
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import mysql.connector

w.start()
pd.set_option('expand_frame_repr', False)
class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        return float(value)

    def _float64_to_mysql(self, value):
        return float(value)

    def _int32_to_mysql(self, value):
        return int(value)

    def _int64_to_mysql(self, value):
        return int(value)


config = {
    'user': 'wudilianghua',
    'host': 'east2-mysql-instance1.cwj25hshjcl1.us-east-2.rds.amazonaws.com',
    'password': 'nbwind123!',
    'database': 'QuantDB'
}

def calTime(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')

def calTime1(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d %H-%M') + timedelta(hours=delta)).strftime('%Y-%m-%d %H-%M')

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
    fm['code'] = fm.index
    fm['datetime'] = indata1.Times[0]
    return fm
def getStockCategyMap(path):
    stockCategory = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            # print (file)
            table = file.split(".")[0]
            category = table.replace("-", '_')
            with open(path + file) as csvDataFile:

                csvReader = csv.reader(csvDataFile)
                for row in csvReader:
                    stock_code = row[1]
                    stockCategory.setdefault(stock_code, []).append(category)
    return stockCategory

class BanKuaiObj(object):
    zdf = 0
    zhanbi = 0
    code = ""



def SortByZhanbiasc(bankuaiList):
    return sorted(bankuaiList, key=lambda x: x.zhanbi, reverse=False)
########################################################
def main():
    dir = "C:/KeLiQuant/WindCategory/"
    import logging
    logging.basicConfig(filename='Bankuai.log', level=logging.DEBUG)
    stockCategory = getStockCategyMap(dir)

    ##############################################
    codeList = getAllStock()
    print (len(codeList))

    codeLists = []
    codeLists.append(codeList[:700])
    codeLists.append(codeList[700:1400])
    codeLists.append(codeList[1400:2100])
    codeLists.append(codeList[2100:2800])
    codeLists.append(codeList[2800:])



    # conn = mysql.connector.connect(**config)
    # conn.set_converter_class(NumpyMySQLConverter)
    #
    # cur = conn.cursor()
    while (1):

        weekno = datetime.today().weekday()
        if weekno in [0, 1, 2, 3, 6]:
            curTime = datetime.today().strftime('%H-%M-%S')
            logging.debug(curTime)
            if (curTime >= '17-35-00' and curTime <= '17-35-59') or (curTime >= '18-00-00' and curTime <= '18-00-59')or (curTime >= '18-30-00' and curTime <= '18-30-59') \
                    or (curTime >= '19-00-00' and curTime <= '19-00-59')or (curTime >= '19-30-00' and curTime <= '19-30-59')or (curTime >= '21-00-00' and curTime <= '21-00-59') \
                    or (curTime >= '21-30-00' and curTime <= '21-30-59')or (curTime >= '22-00-00' and curTime <= '22-00-59')or (curTime >= '22-30-00' and curTime <= '22-30-59') \
                    or (curTime >= '22-43-00' and curTime <= '23-00-59'):
                conn = mysql.connector.connect(**config)
                conn.set_converter_class(NumpyMySQLConverter)


                categoryData = {}
                all_vol = 0
                curTime = datetime.today().strftime('%Y-%m-%d %H-%M')
                curTime = calTime1(curTime, +16)
                logging.debug("BanKuai--" + curTime + " is in processing")

                for code_list in codeLists:
                    parsedStocks = parseStock(code_list)
                    data = conWSQData(w.wsq(parsedStocks, "rt_vol,rt_pct_chg,rt_mkt_cap,rt_float_mkt_cap,rt_insti_activebuy_amt"))
                    # print (data)

                    ct = 1
                    for row in data.itertuples():

                        stock = row[0]
                        if stock not in stockCategory:
                            continue
                        rt_vol =  row[1]
                        rt_pct_chg = row[2] * 100
                        rt_mkt_cap = row[3]
                        rt_float_mkt_cap = row[4]
                        rt_insti_activebuy_amt = row[5]
                        # zhan_bi = rt_vol/rt_float_mkt_cap

                        try:
                            cur = conn.cursor()
                        except:
                            logging.debug("connection is lost 1")
                            conn = mysql.connector.connect(**config)
                            conn.set_converter_class(NumpyMySQLConverter)
                            cur = conn.cursor()
                        query = """INSERT INTO Stock_RT (DATA_DATETIME,STOCK_CODE,ZDF,RT_VOL,rt_insti_activebuy_amt) VALUES (%s,%s,%s,%s,%s)"""
                        try:
                            cur.execute(query, (curTime, stock, rt_pct_chg, rt_vol,rt_insti_activebuy_amt))
                        except:
                            # conn.commit()
                            logging.debug ('exception in loading')
                            continue

                        all_vol = all_vol + rt_vol

                        categories = stockCategory.get(stock)
                        for category in categories:
                            if category not in categoryData:
                                categoryData[category] = [0,0,0,0,0] #rt_pct_chg*rt_float_mkt_cap(0), rt_float_mkt_cap(1), rt_pct_chg*rt_mkt_cap(2),rt_mkt_cap(3),rt_vol(4)
                            catList = categoryData[category]
                            catList[0] = catList[0] + (rt_pct_chg*rt_float_mkt_cap)
                            catList[1] = catList[1] + rt_float_mkt_cap
                            catList[2] = catList[2] + (rt_pct_chg * rt_mkt_cap)
                            catList[3] = catList[3] + rt_mkt_cap
                            catList[4] = catList[4] + rt_vol

                        ct = ct+1
                    print (str(ct)," rows into stock_RT table")
                    conn.commit()
                bankuaiList = []
                for category in categoryData.keys():
                    dataList = categoryData.get(category)
                    zdf = dataList[0]/dataList[1]
                    zhan_bi = dataList[4]/all_vol
                    query = """INSERT INTO BanKuai_RT (DATA_DATETIME,BanKuai,ZDF,Volume_Zhan_Bi,RT_FLOAT_MKT_CAP) VALUES (%s,%s,%s,%s,%s)"""
                    try:
                        cur.execute(query, (curTime, category, zdf, zhan_bi,dataList[1]))
                    except:
                        # conn.commit()
                        logging.debug ('exception in loading bankuai')
                        continue
                    b = BanKuaiObj()
                    b.code = category
                    b.zhanbi = zhan_bi
                    bankuaiList.append(b)
                print(str(ct), " rows into BanKuai_RT table")

                zhanbiSortedList = SortByZhanbiasc(bankuaiList)
                rank = 0
                for bankuai in zhanbiSortedList:
                    query = """INSERT INTO BanKuai_Rank (DATA_DATETIME,BanKuai,Volume_Zhan_Bi) VALUES (%s,%s,%s)"""
                    rank = rank + 1
                    try:
                        cur.execute(query, (curTime, bankuai.code, rank))
                    except:
                        # conn.commit()
                        logging.debug('exception in loading bankuai ranking')
                        continue

                conn.commit()
                conn.close()
        sleep(60)
    # conn.close()
    logging.debug ("done processing")


if __name__ == "__main__": main()