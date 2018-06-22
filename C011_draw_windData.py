import math
from WindPy import *
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import sys
import pandas as pd
def conWSDData(data):
    fm = pd.DataFrame(data.Data, index=data.Fields, columns=data.Times)
    fm = fm.T  # Transpose index and columns
    return fm

def getTDays(offset, passeddate):
    date_data = w.tdaysoffset(offset, passeddate, "")
    try:
        ret_date = (date_data.Data[0][0]).strftime('%Y-%m-%d')
    except:
        print('except')
        print(date_data.Data[0][0])
        print(date_data.Data[0][0].__class__.__name__)
    return ret_date


def main():
    w.start()
    path = 'C:/KeLiQuant/'
    stock = '002690.SZ'
    from_date = '2018-03-01'
    # today = datetime.today().strftime('%Y-%m-%d')
    today = '2018-06-01'


    tomorrow = calTime(today,+1)
    back_days = 15#252

    # args = sys.argv
    # stock = args[1]
    # back_days = int(args[2])

    prev_T_days = getTDays(-back_days+1, from_date)
    stock_name = stock.split('.')[0]
    path = path + stock_name + '-' + str(back_days) + ' Volatility'
    print (stock)
    # print (today)
    # print (back_days)

    timeArray = []
    indexArray = []
    volArrayUp= [0]
    volArrayDown = [0]
    close = []
    open = []
    high = []
    low = []
    macd_data = conWSDData(
        w.wsd(stock, "open,high,low,close", prev_T_days, today, "Fill=Previous;PriceAdj=F"))
    dates = macd_data.index.values
    # print (macd_data)
    for i in range(0,len(dates)-back_days+1):
        timeArray.append(dates[i + back_days-1])
        prices_close = macd_data['CLOSE'].values[i:i + back_days]
        # print(len(prices_close))
        # print (macd_data['OPEN'].values)
        open.append(macd_data['OPEN'].values[i + back_days-1])
        high.append(macd_data['HIGH'].values[i + back_days-1])
        low.append(macd_data['LOW'].values[i + back_days-1])
        close.append(macd_data['CLOSE'].values[i + back_days-1])


        vol = calHistoricalVolatility(prices_close, len(prices_close))
        # print (vol)
        # vol = 2*vol
        volArrayUp.append( prices_close[-1] + vol)
        volArrayDown.append(prices_close[-1] - vol)

    # while from_date <= today:
    #     print (from_date)
    #
    #     back_360_day = calTime(from_date, -100)#500
    #     ts_data = ts.get_hist_data(stock, start=back_360_day, end=from_date,retry_count=5,pause=1)
    #
    #
    #     dates = ts_data.index.values
    #     # print (dates[0])
    #     if dates[0] != from_date:
    #         from_date = calTime(from_date, +1)
    #         continue
    #     timeArray.append(from_date)
    #
    #     price_data_df = ts_data['close'].values
    #     price_data_df = price_data_df[0:back_days]
    #     price_data_df_new = price_data_df[::-1]
    #     print(len(price_data_df))
    #     # print (price_data_df)
    #     # print(price_data_df_new)
    #     open.append(ts_data['open'].values[0])
    #     high.append(ts_data['high'].values[0])
    #     low.append(ts_data['low'].values[0])
    #     close.append(price_data_df[0])
    #
    #
    #     vol = calHistoricalVolatility(price_data_df_new,len(price_data_df_new))
    #     # print (vol)
    #     # vol = abs(vol)
    #     volArrayUp.append(vol+price_data_df[0])
    #     volArrayDown.append(price_data_df[0]-vol)
    #     # print (volArrayUp)
    #     # print (volArrayDown)
    #     from_date = calTime(from_date,+1)
    #
    # print (volArrayUp[-1])
    # print (volArrayDown[-1])
    i = 0
    timeArray.append(tomorrow)
    close.append(0)
    open.append(0)
    high.append(0)
    low.append(0)

    while i < len(timeArray)-2:
        indexArray.append(i)
        i = i + 1



    timeArray = timeArray[1:len(timeArray)-1]
    # indexArray = indexArray[1:len(indexArray)-1]
    volArrayDown = volArrayDown[1:len(volArrayDown)-1]
    volArrayUp = volArrayUp[1:len(volArrayUp)-1]
    close = close[1:len(close)-1]
    open = open[1:len(open)-1]
    high = high[1:len(high)-1]
    low = low[1:len(low)-1]

    # print (len(timeArray))
    # print(len(volArrayDown))
    # print(len(volArrayUp))
    # print(len(close))
    # print(len(open))
    # print(len(high))
    # print(len(low))


    fig = plt.figure(figsize=(40, 20))
    ax = fig.add_subplot(111)
    # ax = fig.add_axes([0.005, 0.55, 1, 0.40])
    ax.set_title(stock + ' Volatility')

    # Create K line
    mpf.candlestick2_ochl(ax, open, close, high, low,
                          width=0.3, colorup='r', colordown='black', alpha=1.0)
    # ax.set_xlim(xmin=0, xmax=400)
    ax.set_xticks(range(0, len(timeArray), 1))
    ax.set_xticklabels(timeArray[::1], rotation=45, fontsize=20)

    ax.plot(indexArray, volArrayUp, c='r', lw=0.5, label='Volatility Up')
    ax.plot(indexArray, volArrayDown, c='black', lw=0.5, label='Volatility Down')

    # drawChart(indexArray,volArrayUp,volArrayDown,close,timeArray,stock + ' Volatility',path+stock + " Volatility")
 # Save the picture
 #    path = path + stock + "-"+ str(back_days) + ' Volatility'
    plt.savefig(path)
    plt.close()

def drawChart(indexArray, volArrayUp,volArrayDown,close,timeArray,name,path):
    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(111)
    ax1.plot(indexArray, volArrayUp, c='r', lw=0.5, label='Volatility Up')
    ax1.plot(indexArray, volArrayDown, c='black', lw=0.5, label='Volatility Down')
    ax1.plot(indexArray, close, '--',c='blue', lw=0.5, label='Close')
    ax2 = ax1.twinx()
    ax1.set_xticks(range(0, len(timeArray), 1))
    ax1.set_xticklabels(timeArray[::1], rotation=90)
    ax1.grid(True)

    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc='upper left')

    ax1.set_title(name)
    plt.savefig(path)
    plt.close()


def calTime(original_datetime, delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')

def calHistoricalVolatility(prices, period):
    dailyReturn = []
    for i in range(1, period):
        dailyReturn.append(prices[i] / prices[i-1])

    returnMean = sum(dailyReturn) / period

    diff = []
    for i in range(0, period-1):
        diff.append(math.pow((dailyReturn[i] - returnMean), 2))

    vol = math.sqrt(sum(diff) / (period - 2)) * math.sqrt(246/(period-1))

    return vol
def calHistoricalVolatility_v2():
    # Load the required modules and packages
    import numpy as np
    import pandas

    # import pandas.io.data as web

    # Pull NIFTY data from Yahoo finance
    NIFTY = ts.get_hist_data('600460', start='2017-11-01', end='2017-12-12')

    # Compute the logarithmic returns using the Closing price
    NIFTY['Log_Ret'] = np.log(NIFTY['close'] / NIFTY['close'].shift(1))

    # Compute Volatility using the pandas rolling standard deviation function
    NIFTY['Volatility'] = pandas.Series.rolling(window=252,center=False).std(NIFTY['Log_Ret'], window=252) * np.sqrt(252)

    close = NIFTY['close'].values
    vol = NIFTY['Volatility'].values

    print (close)
    print (vol)

    # print(NIFTY.tail(15))

    # Plot the NIFTY Price series and the Volatility
    # NIFTY[['Close', 'Volatility']].plot(subplots=True, color='blue', figsize=(8, 6))

if __name__ == "__main__": main()