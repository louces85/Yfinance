import subprocess
import sys
import os
import datetime
from dateutil.relativedelta import relativedelta
import yfinance

from dao.stocksDAO import StocksDAO

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import json
from enums.rules import Rules

class Valuation:

    def __init__(self, ticker , name_json_file):
        self.ticker = ticker
        self.name_json_file = name_json_file

    def get_list_stoks(self):
        with open(self.name_json_file, encoding='utf-8') as json_file:
            list_dict_stoks = json.load(json_file)
            return list_dict_stoks

    def get_dict_indicators(self):
        list = self.get_list_stoks() 
        dict_json = {}
        
        for l in list:
            if l['ticker'] == self.ticker:
                dict_json = l
                break
        
        dict_stock = {
                'Ticker':    dict_json.get('ticker', '-'),
                'D.Y':       dict_json.get('dy', '-'),
                'P/L':       dict_json.get('p_L', '-'),
                'P/VP':      dict_json.get('p_VP', '-'),
                'VPA':       dict_json.get('vpa', '-'),
                'P/A':       dict_json.get('passivo_Ativo', '-'),
                'DL/PL':     dict_json.get('dividaliquidaPatrimonioLiquido', '-'),
                'DL/EBITDA': dict_json.get('dividaLiquidaEbit', '-'),
                'LQ':        dict_json.get('liquidezCorrente', '-'),    
                'M.EBIT':    dict_json.get('margemEbit', '-'),
                'M.L':       dict_json.get('margemLiquida', '-'),
                'ROE':       dict_json.get('roe', '-'),
                'ROIC':      dict_json.get('roic', '-'),
                'CAGR.R':    dict_json.get('receitas_Cagr5', '-'),
                'CAGR.L':    dict_json.get('lucros_Cagr5', '-'),
                'Rank' :     0,
                'flagVPA':   False
        }

        try:
            #stock = Stock(dict_stock['Ticker'].upper())
            stk_DAO = StocksDAO()
            price_now = stk_DAO.get_price(dict_stock['Ticker'].upper())
            if price_now <= float(dict_stock['VPA']):
                dict_stock['flagVPA'] = True
        except ValueError:
            pass
        
        dict_stock['Rank'] = self.calc_ranking_indicators(dict_stock)

        for key in dict_stock.keys():
            flag = key != 'Ticker' and key != 'flagVPA' and dict_stock[key] != '-'
            if flag:
                dict_stock[key] = round(float(dict_stock[key]),2)

        return dict_stock

    def calc_ranking_indicators(self, dict_stock):
        rank = 0
        self.dict_stock  = dict_stock

        try:
            #stock = Stock(self.dict_stock['Ticker'].upper())
            stk_DAO = StocksDAO()
            price_now = stk_DAO.get_price(dict_stock['Ticker'].upper())
            if price_now <= float(self.dict_stock['VPA']):
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['D.Y']) >= Rules.D_Y.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['P/L']) <= Rules.P_L.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['P/VP']) <= Rules.P_VP.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['DL/PL']) <= Rules.DL_PL.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['DL/EBITDA']) <= Rules.DL_EBITDA.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['P/A']) <= Rules.P_A.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['LQ']) >= Rules.L_Q.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['M.EBIT']) >= Rules.M_EBIT.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['M.L']) >= Rules.M_L.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['ROE']) >= Rules.ROE.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['ROIC']) >= Rules.ROIC.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['CAGR.R']) >= Rules.CAGR_R.value:
                rank += 1
        except ValueError:
            pass

        try:
            if float(dict_stock['CAGR.L']) >= Rules.CAGR_L.value:
                rank += 1
        except ValueError:
            pass

        return rank
    
    def get_payout(self):
        
        format_str = "curl -s https://statusinvest.com.br/acao/payoutresult?code=" + self.ticker.strip().lower() + " | grep 'actual' | awk -F ':' '{print $3}' | awk -F ',' '{print $1}'"
        payout = subprocess.getoutput(format_str)
        
        try:
            return round(float(payout),2) if round(float(payout),2) > 0 else 0 
        except ValueError:
            return 0
        except ZeroDivisionError:
            return 0
        except AttributeError:
            return 0
    
    def get_average_dividends_four_years(self):
        
        years = []

        for y in range(4):
            year = (datetime.datetime.now()-relativedelta(years=(y+1))).strftime("%Y")
            years.append(year)
        
        msft = yfinance.Ticker(self.ticker + '.SA')
    
        history_dividends = msft.dividends
        sum_dividends = 0
        count_years   = 0

    
        try:
            for year in years:
                
                flag = False
                for k in history_dividends.keys():
                    if(str(k).find(year) == 0):
                        flag = True
                        sum_dividends += float(history_dividends.get(k))
                
                if flag == True:
                    count_years += 1
            return float(sum_dividends/count_years)
        except ValueError:
            return 0
        except ZeroDivisionError:
            return 0
        except AttributeError:
            return 0 

    def get_price_target(self):
        try:
            return round(self.get_average_dividends_four_years()/Rules.BASIN.value,2)
        except ValueError:
            return 0
        except ZeroDivisionError:
            return 0
        except TypeError:
            return 0