import talib
from numpy import array
prices = array([15.2,12.3,18.2])
short_avg = talib.SMA(prices,20)
print (short_avg)