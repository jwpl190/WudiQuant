import tushare as ts
import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import collections
import csv
from time import sleep
import os
def sendEmail(fullpath, file, title):
    fromaddr = "keli4660@gmail.com"
    toaddr = "392949291@qq.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = title
    filename = file
    attachment = open(fullpath, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "nbwind123")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()



def calTime(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')

def calTimeHour(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d %H-%M') + timedelta(hours=delta)).strftime(
        '%Y-%m-%d %H-%M')

data_dir = "C:/KeLiQuant/c006_output/"
output_dir = "C:/KeLiQuant/c006_toFeng/"
dir = "C:/KeLiQuant/"

stock_codes = pd.read_csv(dir + 'codeList.txt', dtype=str)['stock'].values

while 1:
    weekno = datetime.today().weekday()
    if weekno in [0,1, 2, 3, 4]:#Monday is 0
        dateTime = datetime.today().strftime('%Y-%m-%d %H-%M')
        curTime = dateTime.split(' ')[1]
        curDate = dateTime.split(' ')[0]
        if '17-00' in curTime:
            list = []
            for stock in stock_codes:
                print(stock)

                # print (curDate)
                # Get history prices
                price_data_df = ts.get_hist_data(stock, start=curDate, end=curDate,retry_count=10,pause=2)
                if price_data_df is None or len(price_data_df) == 0:
                    continue
                price_data_df.sort_index(inplace=True)
                try:
                    cur_price_low = price_data_df['low'].values[-1]
                except:
                    print (price_data_df)
                cur_price_high = price_data_df['high'].values[-1]
                ma5 = price_data_df['ma5'].values[-1]
                if cur_price_low < ma5 and cur_price_high > ma5:
                    list.append(stock)
            filename = curDate + "_C006_daily_output.csv"
            fullpath = data_dir + filename

            with open(fullpath, "w") as output:
                writer = csv.writer(output, lineterminator='\n')
                for stock in list:
                    writer.writerow([stock])
            ##Get history files
            target_files = []
            for root, dirs, files in os.walk(data_dir):
                files.sort(reverse=True)
                for file in files:
                    if (len(target_files) < 5):
                        target_files.append(file)
            print(target_files)



            stock_lists = []
            for file in target_files:
                list = []
                with open(data_dir + file) as csvDataFile:
                    csvReader = csv.reader(csvDataFile)
                    for row in csvReader:
                        stock = row[0]
                        list.append(stock)
                    stock_lists.append(list)

            # check ma5 of 1st day and 5th day
            first_day = target_files[-1].split('_')[0]
            fifth_day = target_files[0].split('_')[0]

            res = []
            for stock in stock_lists[0]:
                if stock in stock_lists[1] and stock in stock_lists[2] and stock in stock_lists[3] and \
                        stock_lists[4]:
                    price_data_df = ts.get_hist_data(stock, start=first_day, end=fifth_day,retry_count=10,pause=2)
                    price_data_df.sort_index(inplace=True)
                    firstday_ma5 = price_data_df['ma5'].values[0]
                    fifthday_ma5 = price_data_df['ma5'].values[-1]
                    if (fifthday_ma5 > firstday_ma5):
                         factor = ((price_data_df['high'].values[-1] - price_data_df['low'].values[-1]) + (price_data_df['high'].values[-2] - price_data_df['low'].values[-2])
                         +(price_data_df['high'].values[-3] - price_data_df['low'].values[-3]))/3/price_data_df['close'].values[-1]
                         if factor > 0.05:
                            res.append(stock)

            filename = curDate + "_C006_output.csv"
            fullpath = output_dir + filename

            with open(fullpath, "w") as output:
                writer = csv.writer(output, lineterminator='\n')
                for val in res:
                    writer.writerow([val])
            sendEmail(fullpath, filename, curDate + "_C006_report")
            print ('done')
            exit(0)

    sleep(57)