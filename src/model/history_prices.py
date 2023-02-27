"""
-----------------------------------------------------------------------------
@copyright 2021 Fabiano Louzada
@doc Analyze B3 stocks List
@author Fabiano Louzada Cesario <fabiano.cesario.k@gmail.com>
@yfinance 1.0
-----------------------------------------------------------------------------
"""

import yfinance as yf
import warnings
from pandas.core.common import SettingWithCopyWarning
import sys
import os
from prettytable import PrettyTable
from tqdm import tqdm
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from jdbc.connection_factory import Connection_Factory
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

def get_all_stocks():
    conn = Connection_Factory().connection() 

    cur = conn.cursor()
    #cur.execute("select * from  history where net_income and date_update != '2022-06-04';")
    cur.execute("select * from history where net_income = true;")


    list = cur.fetchall()
    cur.close()

    conn.commit()
    conn.close

    list_stocks = []
    for stock in list:
      list_stocks.append(stock[1])
    
    return list_stocks

def uptate_history_stock(price_min, price_max, net_income, ticker):
    conn = Connection_Factory().connection()
    
    cur = conn.cursor()
    cur.execute("update history set price_min={}, price_max={}, net_income={}, date_update=CURRENT_DATE where ticker like '{}';".format(price_min, price_max,net_income, ticker))
    cur.close()

    conn.commit()
    conn.close

get_all_stocks()

myTable = PrettyTable(["Ticker", "pMax", "pMin", "Net Income"])
myTable.align["Ticker"] = "l"

for stock in tqdm(get_all_stocks()):
    df_six_month = yf.download(stock + '.SA', period='6mo', progress=False, show_errors=True)
    df_prices = df_six_month[['Adj Close']]
    df_prices.dropna(subset = ['Adj Close'], inplace=True) #remove values NaN
    cols_as_np_v = df_prices[df_prices.columns[0:]].to_numpy()
    
    print(df_six_month)
    
    flag = True
    try:
        msft = yf.Ticker(stock + '.SA')
        df = msft.financials
        if not df.empty:
            row = df.loc['Net Income', :]
            list_incomes = row.tolist()
        
            for i in list_incomes:
                if i < 0:
                    flag = False
                    break
            
    except Exception as e:
        print(e)
        flag = True
       
    try:
        highest_price_in_the_last_six_months = round(cols_as_np_v.max(),1)
        lowest_price_in_the_last_six_months = round(cols_as_np_v.min(),1)
    except Exception as e:
        highest_price_in_the_last_six_months = -1
        lowest_price_in_the_last_six_months  = -1
    
    
    myTable.add_row([stock, str(highest_price_in_the_last_six_months), str(lowest_price_in_the_last_six_months),str(flag)])  
    if(len(df_six_month) > 1):
        uptate_history_stock(lowest_price_in_the_last_six_months, highest_price_in_the_last_six_months, flag , stock)
    else:
        uptate_history_stock(lowest_price_in_the_last_six_months, highest_price_in_the_last_six_months, flag, stock)

print(myTable)