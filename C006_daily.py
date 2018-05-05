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

data_dir = "C:/KeLiQuant/"
output = "C:/KeLiQuant/output/"


today = datetime.today().strftime('%Y-%m-%d')
# back_day = calTime(today, -200)
today = '2018-04-13'
print("today: " + today)
# print("back  day: " + back_day)



stock_codes = pd.read_csv(data_dir + 'codeList.txt', dtype=str)['stock'].values
df = []
# stock_codes=['600699','603998','603997']

while 1:
    weekno = datetime.today().weekday()
    if weekno in [1, 2, 3, 4, 5,6]:
        dateTime = datetime.today().strftime('%Y-%m-%d %H-%M')
        dateTime = calTimeHour(dateTime, +15)
        curTime = dateTime.split(' ')[1]
        if '20-00' in curTime or curTime > '00-00':
            for stock in stock_codes:
                print(stock)
                # Get history prices
                price_data_df = ts.get_hist_data(stock, start=today, end=today)
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

                    d = {'stock': stock,
                         'MA 5': ma5,
                         'low': cur_price_low,
                         "high": cur_price_high
                         }

                    df.append(d)
            df = pd.DataFrame(df)
            filename = today + "_C006_daily_output.csv"
            fullpath = output + filename
            df.to_csv(fullpath, index=False, columns=["stock", "MA 5", "low", "high"])

            # sendEmail(fullpath, filename, today + "_C006_report")
        exit(0)