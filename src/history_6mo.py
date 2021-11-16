"""
-----------------------------------------------------------------------------
@copyright 2021 Fabiano Louzada
@doc Analyze B3 stocks List
@author Fabiano Louzada Cesario <fabiano.cesario.k@gmail.com>
@yfinance 1.0
-----------------------------------------------------------------------------
"""

import yfinance as yf

file_in  = open('files/stocks_file', 'r')
file_out = open('files/history_6mo_results_net_income', 'w')

for stk in file_in:
    df_six_month = yf.download(stk.strip()+'.SA', period='6mo', progress=False)
    df_prices = df_six_month[['Adj Close']]
    df_prices.dropna(subset = ['Adj Close'], inplace=True) #remove values NaN
    cols_as_np_v = df_prices[df_prices.columns[0:]].to_numpy()
    
    
    flag = True
    try:
        msft = yf.Ticker(stk.strip()+'.SA')
        df = msft.financials
        
        row = df.loc['Net Income', :]
        list_incomes = row.tolist()
        
        print(list_incomes)
        
        for i in list_incomes:
            if i < 0:
                print(f'{stk.strip()} fail in net income test')
                flag = False
                break
            
                
    except Exception as e:
        print(e)
        flag = True
       
    try:
        highest_price_in_the_last_six_months = round(cols_as_np_v.max(),1)
        lowest_price_in_the_last_six_months = round(cols_as_np_v.min(),1)
    except Exception as e:
        highest_price_in_the_last_six_months = 10000
        lowest_price_in_the_last_six_months  = 10000
    
    
    str_out = f"{stk.strip()+'.SA'}\tMAX\t{highest_price_in_the_last_six_months}\tMIN\t{lowest_price_in_the_last_six_months}\tNET Income\t{flag}\n"
    if(len(df_six_month) > 1):
        file_out.write(str_out)
        print(str_out.strip())
    else:
        str_out = f"{stk.strip()+'.SA'}\tMAX\t{10000}\tMIN\t{10000}\tNET Income\t{flag}\n"
        file_out.write(str_out)
        print(str_out.strip())
    