# coding=utf-8
import easytrader
import pandas as pd
from time import sleep
user = easytrader.use('ths')

import datetime

# balance_list = []
# balance_list.append(user.balance)
# user_balance = pd.DataFrame(balance_list)
# print (user_balance)

# user.connect('C:/同花顺软件/同花顺/xiadan.exe')
# buy_ret = user.buy('002690', price=21.48, amount=100)
# curTime = datetime.datetime.today().strftime('%Y-%m-%d %H-%M-%S')
# print (curTime)
# print (buy_ret)

# user.connect('C:/同花顺软件/同花顺/xiadan.exe')
# user_today_entrust = pd.DataFrame(user.today_entrusts)
# one_stock = user_today_entrust.loc[(user_today_entrust['证券代码'] == '002690')]
# one_stock = one_stock.sort_values('委托时间')
# print (one_stock)
# print (user_today_entrust)
# user.exit()
# cancel_ret = user.cancel_entrust('906217370')
# print (cancel_ret)

user.connect('C:/同花顺软件/同花顺/xiadan.exe')
user_position = pd.DataFrame(user.position)
print (user_position)

user.connect('C:/同花顺软件/同花顺/xiadan.exe')
user_today_entrust = pd.DataFrame(user.today_entrusts)
one_stock = user_today_entrust.loc[(user_today_entrust['证券代码'] == '002690')]
buy_trades = one_stock.loc[(one_stock['操作'] == '买入') & (one_stock['备注'] == '全部成交')]
buy_amount = buy_trades['成交数量'].sum()
print (buy_amount)
sell_trades = one_stock.loc[(one_stock['操作'] == '卖出')& (one_stock['备注'] == '全部成交')]
sell_amount = sell_trades['成交数量'].sum()
print (sell_amount)
position = buy_amount - sell_amount
print (position)

user.connect('C:/同花顺软件/同花顺/xiadan.exe')
user_today_trades = pd.DataFrame(user.today_trades)
print (user_today_trades)
one_stock = user_today_trades.loc[(user_today_trades['证券代码'] == '002690')]
buy_trades = one_stock.loc[(one_stock['操作'] == '买入')]
buy_amount = buy_trades['成交数量'].sum()
print (buy_amount)
sell_trades = one_stock.loc[(one_stock['操作'] == '卖出')]
sell_amount = sell_trades['成交数量'].sum()
print (sell_amount)
position = buy_amount - sell_amount

# print (position)


# user.connect('C:/同花顺软件/同花顺/xiadan.exe')
# user_position = pd.DataFrame(user.position)
# print (user_position)

