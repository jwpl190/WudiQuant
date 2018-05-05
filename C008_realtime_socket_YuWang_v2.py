from WindPy import *
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import tushare as ts
import mysql.connector
import math
import requests


pd.set_option('expand_frame_repr', False)

def calTime1(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')


def calHistoricalVolatility(prices, period):
    dailyReturn = []
    for i in range(1, period):
        dailyReturn.append(prices[i] / prices[i - 1])

    returnMean = sum(dailyReturn) / period

    diff = []
    for i in range(0, period - 1):
        diff.append(math.pow((dailyReturn[i] - returnMean), 2))

    vol = math.sqrt(sum(diff) / (period - 2)) * math.sqrt(246 / (period - 1))

    return vol

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

import logging
logging.basicConfig(filename='ZJL.log',level=logging.DEBUG)


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

data_dir = "C:/KeLiQuant/"
stock_codes = pd.read_csv(data_dir + 'stockCodes',dtype=str)['stock'].values
parsed_stock_codes = parseStock(stock_codes)

# conn = mysql.connector.connect(**config)
# conn.set_converter_class(NumpyMySQLConverter)
#
# logging.debug ("connected")

def calTime(original_datetime, delta):

    return (datetime.strptime(original_datetime, '%Y-%m-%d %H-%M-%S') + timedelta(hours=delta)).strftime('%Y-%m-%d %H-%M-%S')

def conWSETData(indata1):
    fm = pd.DataFrame(indata1.Data, index=indata1.Fields, columns=indata1.Times)
    fm = fm.T  # Transpose index and columns
    return fm

# calVolDay= '2017-01-01'
stock_vol_backdays = {}
stock_vol_backdays['002049.SZ'] = 5
stock_vol_backdays['002153.SZ'] = 6
stock_vol_backdays['600835.SH'] = 6
stock_vol_backdays['000830.SZ'] = 10
stock_vol_backdays['600507.SH'] = 10
stock_vol_backdays['600516.SH'] = 10
stock_vol_backdays['601015.SH'] = 10
stock_vol_backdays['002466.SZ'] = 5
stock_vol_backdays['000938.SZ'] = 5
stock_vol_backdays['600438.SH'] = 10
stock_vol_backdays['000792.SZ'] = 10
stock_vol_backdays['002230.SZ'] = 4
stock_vol_backdays['600460.SH'] = 10
stock_vol_backdays['000651.SZ'] = 7
stock_vol_backdays['600699.SH'] = 7
stock_vol_backdays['300055.SZ'] = 12


while (1):
    weekno = datetime.today().weekday()
    if weekno in [0,1,2,3,4]:
        curTime = datetime.today().strftime('%H-%M-%S')
        if (curTime >= '09-00-00' and curTime <= '09-00-59'):
            curDay = datetime.today().strftime('%Y-%m-%d')


            print ('processing volatility for ', curDay)
            stock_vol = {}
            yesterday = calTime1(curDay, -1)

            conn = mysql.connector.connect(**config)
            conn.set_converter_class(NumpyMySQLConverter)
            cur = conn.cursor()

            for stock in stock_vol_backdays.keys():
                back_days = stock_vol_backdays.get(stock)
                from_date = yesterday
                back_360_day = calTime1(from_date, -30)  # 500
                stock_tushare = stock.split(".")[0]
                ts_data = ts.get_hist_data(stock_tushare, start=back_360_day, end=from_date)
                price_data_df = ts_data['close'].values
                price_data_df = price_data_df[0:back_days]
                price_data_df_new = price_data_df[::-1]
                vol = calHistoricalVolatility(price_data_df_new, len(price_data_df_new))
                vol_pctg = vol/price_data_df[0]
                query = """INSERT INTO Stock_Volatility (DATA_DATE,STOCK_CODE,volatility,volatility_pctg) VALUES (%s,%s,%s,%s)"""
                try:
                    cur.execute(query, (curDay, stock, vol,vol_pctg))
                except:
                    # conn.commit()
                    print ('except in volatility')
                    continue
                stock_vol[stock] = vol
            conn.commit()
            conn.close()
        # print (stock_vol)

        # curTime = datetime.today().strftime('%H-%M-%S')
        # logging.debug(curTime)
        elif(curTime >= '09-30-00' and curTime <= '11-30-59') or (curTime >= '13-00-00' and curTime <= '15-00-59'):
            w.start()
            curTime = datetime.today().strftime('%Y-%m-%d %H-%M-%S')

            logging.debug("ZJL--" + curTime + " is in processing")
            # print (curTime + " is in processing")
            try:
                data = conWSQData(w.wsq(parsed_stock_codes,'rt_insti_inflow,rt_vip_inflow,rt_mid_inflow,rt_indi_inflow,rt_bidvol,rt_askvol,'
                                          'rt_bsize_total ,rt_asize_total,rt_insti_activebuy_amt,rt_vip_activebuy_amt,rt_mid_activebuy_amt,'
                                          'rt_indi_activebuy_amt,rt_insti_activesell_amt,rt_vip_activesell_amt,rt_mid_activesell_amt,rt_indi_activesell_amt,rt_last,rt_downward_vol,rt_upward_vol'))

            except:
                print ('except 1')
                continue


            # msgToSend = []
            for stock in stock_codes:
                try:
                    cur_data = data.loc[(data['code'] == stock)]
                    rt_insti_inflow = cur_data['RT_INSTI_INFLOW'].values[0]
                    rt_vip_inflow = cur_data['RT_VIP_INFLOW'].values[0]
                    rt_mid_inflow = cur_data['RT_MID_INFLOW'].values[0]
                    rt_indi_inflow = cur_data['RT_INDI_INFLOW'].values[0]
                    rt_bidvol = cur_data['RT_BIDVOL'].values[0]
                    rt_askvol = cur_data['RT_ASKVOL'].values[0]
                    rt_bsize_total = cur_data['RT_BSIZE_TOTAL'].values[0]
                    rt_asize_total = cur_data['RT_ASIZE_TOTAL'].values[0]
                    rt_insti_activebuy_amt = cur_data['RT_INSTI_ACTIVEBUY_AMT'].values[0]
                    rt_vip_activebuy_amt= cur_data['RT_VIP_ACTIVEBUY_AMT'].values[0]
                    rt_mid_activebuy_amt = cur_data['RT_MID_ACTIVEBUY_AMT'].values[0]
                    rt_indi_activebuy_amt = cur_data['RT_INDI_ACTIVEBUY_AMT'].values[0]
                    rt_insti_activesell_amt = cur_data['RT_INSTI_ACTIVESELL_AMT'].values[0]
                    rt_vip_activesell_amt = cur_data['RT_VIP_ACTIVESELL_AMT'].values[0]
                    rt_mid_activesell_amt = cur_data['RT_MID_ACTIVESELL_AMT'].values[0]
                    rt_indi_activesell_amt = cur_data['RT_INDI_ACTIVESELL_AMT'].values[0]
                    rt_last = cur_data['RT_LAST'].values[0]
                    rt_downward_vol = cur_data['RT_DOWNWARD_VOL'].values[0]
                    rt_upward_vol = cur_data['RT_UPWARD_VOL'].values[0]


                except:
                    continue
                # if float(rt_asize_total) != 0 and float(rt_bsize_total) != 0:
                #     if float(rt_bsize_total)/float(rt_asize_total) >=5:
                #         msg = {}
                #         msg['stock'] = stock
                #         msg['time'] = curTime
                #         msg['weiBuy'] = rt_bsize_total
                #         msg['weiSell'] = rt_asize_total
                #         msg['ratio'] = float(rt_bsize_total)/float(rt_asize_total)
                #         msg['result'] = 'BBBBBBBBBBB'
                #         # if stock_vol.has_key(stock):
                #         if stock in stock_vol:
                #             msg['Volatility'] = stock_vol.get(stock)
                #         else:
                #             msg['Volatility'] = 'Empty'
                #         msgToSend.append(msg)
                #     elif float(rt_asize_total)/float(rt_bsize_total) >=5:
                #         msg = {}
                #         msg['stock'] = stock
                #         msg['time'] = curTime
                #         msg['weiBuy'] = rt_bsize_total
                #         msg['weiSell'] = rt_asize_total
                #         msg['ratio '] = float(rt_asize_total) / float(rt_bsize_total)
                #         msg['result'] = 'SSSSSSSSSSS'
                #         # if stock_vol.has_key(stock):
                #         if stock in stock_vol:
                #             msg['Volatility'] = stock_vol.get(stock)
                #         else:
                #             msg['Volatility'] = 'Empty'
                #         msgToSend.append(msg)

                try:
                    cur = conn.cursor()
                except:
                    logging.debug ('ZJL--Connection to database has been lost')
                    conn = mysql.connector.connect(**config)
                    conn.set_converter_class(NumpyMySQLConverter)

                    logging.debug ('ZJL--reconnected to database')
                    cur = conn.cursor()

                query = """INSERT INTO Stock_ZJL (DATA_DATETIME,STOCK_CODE,LAST_PRICE,rt_bidvol,rt_askvol,rt_bsize_total,rt_asize_total,rt_insti_inflow,rt_vip_inflow,rt_mid_inflow,
                rt_indi_inflow,rt_insti_activebuy_amt,rt_vip_activebuy_amt,rt_mid_activebuy_amt,rt_indi_activebuy_amt,rt_insti_activesell_amt,rt_vip_activesell_amt,rt_mid_activesell_amt,
                rt_indi_activesell_amt,rt_downward_vol,rt_upward_vol) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                try:
                    cur.execute(query, (curTime, stock, rt_last, rt_bidvol, rt_askvol, rt_bsize_total, rt_asize_total, rt_insti_inflow, rt_vip_inflow, rt_mid_inflow,
                                        rt_indi_inflow,rt_insti_activebuy_amt,rt_vip_activebuy_amt,rt_mid_activebuy_amt,rt_indi_activebuy_amt,rt_insti_activesell_amt,
                                        rt_vip_activesell_amt,rt_mid_activesell_amt,rt_indi_activesell_amt,rt_downward_vol,rt_upward_vol))

                except:
                    conn.commit()
                    continue
            # print (msgToSend)
            # if len(msgToSend) > 0:
            #     requests.post('http://18.216.249.24:80/weimaiAlertProc', json=msgToSend)
            conn.commit()
            logging.debug("ZJL--done loading")
            w.stop()
        # elif (curTime >= '05-00-00' and curTime <= '05-00-59'):
        #     w.start()
        #     curTime = datetime.today().strftime('%Y-%m-%d %H-%M-%S')
        #     curTime = calTime(curTime, +16)
        #     logging.debug("HGT--start processing HGT")
        #     logging.debug("HGT--" + curTime)
        #     today = datetime.today().strftime('%Y-%m-%d')
        #
        #     try:
        #         shhk_data = conWSETData(w.wset("shhktransactionstatistics",
        #                                        "startdate=" + today + ";enddate=" + today + ";cycle=day;currency=cny;field=sh_net_purchases,hk_net_purchases"))
        #         shhk_sh_net_purchases = shhk_data['sh_net_purchases'].values[0]
        #         shhk_hk_net_purchases = shhk_data['hk_net_purchases'].values[0]
        #
        #         szhk_data = conWSETData(w.wset("szhktransactionstatistics",
        #                                        "startdate=" + today + ";enddate=" + today + ";cycle=day;currency=cny;field=sz_net_purchases,hk_net_purchases"))
        #         szhk_sz_net_purchases = szhk_data['sz_net_purchases'].values[0]
        #         szhk_hk_net_purchases = szhk_data['hk_net_purchases'].values[0]
        #
        #     except:
        #         logging.debug("HGT--failed to query HGT data")
        #         sleep(30)
        #         continue
        #
        #     # logging.debug(shhk_sh_net_purchases)
        #     # logging.debug(shhk_hk_net_purchases)
        #     # logging.debug(szhk_sz_net_purchases)
        #     # logging.debug(szhk_hk_net_purchases)
        #     try:
        #         cur = conn.cursor()
        #     except:
        #         logging.debug('HGT--Connection to database has been lost')
        #         conn = mysql.connector.connect(**config)
        #         conn.set_converter_class(NumpyMySQLConverter)
        #
        #         logging.debug('HGT--reconnected to database')
        #         cur = conn.cursor()
        #
        #     query = """INSERT INTO Stock_HGT (DATA_DATETIME,shhk_sh_net_purchases,shhk_hk_net_purchases,szhk_sz_net_purchases,szhk_hk_net_purchases) VALUES (%s,%s,%s,%s,%s)"""
        #     try:
        #         cur.execute(query, (
        #             today, shhk_sh_net_purchases, shhk_hk_net_purchases, szhk_sz_net_purchases, szhk_hk_net_purchases))
        #
        #     except:
        #         # conn.commit()
        #         logging.debug("HGT--failed to load HGT data")
        #     conn.commit()
        #     logging.debug("HGT--done loading")
        #     w.stop()
    sleep(60)



