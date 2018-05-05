from WindPy import *
import pandas as pd
import numpy as np
from time import sleep
import os
import csv
import mysql.connector


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
    w.start()
    codeList = getAllStock()
    print (len(codeList))
    w.stop()
    codeLists = []
    codeLists.append(codeList[:500])
    codeLists.append(codeList[500:1000])
    codeLists.append(codeList[1000:1500])
    codeLists.append(codeList[1500:2000])
    codeLists.append(codeList[2000:2500])
    codeLists.append(codeList[2500:3000])
    codeLists.append(codeList[3000:])



    # conn = mysql.connector.connect(**config)
    # conn.set_converter_class(NumpyMySQLConverter)
    #
    # cur = conn.cursor()
    while (1):

        weekno = datetime.today().weekday()
        if weekno in [0, 1, 2, 3, 4]:
            curTime = datetime.today().strftime('%H-%M-%S')
            logging.debug(curTime)
            if (curTime >= '09-35-00' and curTime <= '09-35-59') or (curTime >= '10-00-00' and curTime <= '10-00-59')or (curTime >= '10-30-00' and curTime <= '10-30-59') \
                    or (curTime >= '11-00-00' and curTime <= '11-00-59')or (curTime >= '11-30-00' and curTime <= '11-30-59')or (curTime >= '13-00-00' and curTime <= '13-00-59') \
                    or (curTime >= '13-30-00' and curTime <= '13-30-59')or (curTime >= '14-00-00' and curTime <= '14-00-59')or (curTime >= '14-30-00' and curTime <= '14-30-59') \
                    or (curTime >= '15-00-00' and curTime <= '15-00-59'):
                w.start()
                conn = mysql.connector.connect(**config)
                conn.set_converter_class(NumpyMySQLConverter)


                categoryData = {}
                all_vol = 0
                curTime = datetime.today().strftime('%Y-%m-%d %H-%M')
                logging.debug("BanKuai--" + curTime + " is in processing")

                for code_list in codeLists:
                    parsedStocks = parseStock(code_list)
                    data = conWSQData(w.wsq(parsedStocks, "rt_vol,rt_pct_chg,rt_mkt_cap,rt_float_mkt_cap,rt_insti_activebuy_amt,rt_amt"))
                    # print (data)
                    inserted = []
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
                        rt_amt = row[6]
                        # zhan_bi = rt_vol/rt_float_mkt_cap
                        inserted.append((curTime, stock, rt_pct_chg, rt_vol,rt_insti_activebuy_amt,rt_amt))

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
                    # print (inserted)
                    try:
                        cur = conn.cursor()
                    except:
                        logging.debug("connection is lost 1")
                        conn = mysql.connector.connect(**config)
                        conn.set_converter_class(NumpyMySQLConverter)
                        cur = conn.cursor()
                    query = """INSERT INTO Stock_RT (DATA_DATETIME,STOCK_CODE,ZDF,RT_VOL,rt_insti_activebuy_amt,RT_AMT) VALUES (%s,%s,%s,%s,%s,%s)"""
                    try:
                        cur.executemany(query, inserted)
                    except:
                        # conn.commit()
                        logging.debug('exception in loading')
                        continue

                    # print (str(ct)," rows into stock_RT table")
                    conn.commit()

                bankuaiList = []
                ct=1
                inserted = []
                for category in categoryData.keys():
                    ct = ct+1

                    dataList = categoryData.get(category)
                    zdf = dataList[0]/dataList[1]
                    zhan_bi = dataList[4]/all_vol
                    inserted.append((curTime, category, zdf, zhan_bi,dataList[1]))

                    b = BanKuaiObj()
                    b.code = category
                    b.zhanbi = zhan_bi
                    bankuaiList.append(b)
                query = """INSERT INTO BanKuai_RT (DATA_DATETIME,BanKuai,ZDF,Volume_Zhan_Bi,RT_FLOAT_MKT_CAP) VALUES (%s,%s,%s,%s,%s)"""
                try:
                    cur.executemany(query,inserted)
                except:
                    # conn.commit()
                    logging.debug('exception in loading bankuai')
                    continue
                conn.commit()
                # print(str(ct), " rows into BanKuai_RT table")

                zhanbiSortedList = SortByZhanbiasc(bankuaiList)
                rank = 0
                ct = 1
                inserted = []
                for bankuai in zhanbiSortedList:
                    ct = ct+1
                    rank = rank + 1
                    inserted.append((curTime, bankuai.code, rank))
                query = """INSERT INTO BanKuai_Rank (DATA_DATETIME,BanKuai,Volume_Zhan_Bi) VALUES (%s,%s,%s)"""
                try:
                    cur.executemany(query, inserted)
                except:
                    # conn.commit()
                    logging.debug('exception in loading bankuai ranking')
                    continue
                # print(str(ct), " rows into BanKuai_Rank table")
                conn.commit()
                conn.close()
                w.stop()
        sleep(60)
    # conn.close()
    logging.debug ("done processing")


if __name__ == "__main__": main()