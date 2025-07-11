"""
-----------------------------------------------------------------------------
@copyright 2021 Fabiano Louzada
@doc Analyze B3 stocks List
@author Fabiano Louzada Cesario <fabiano.cesario.k@gmail.com>
@yfinance 1.0
-----------------------------------------------------------------------------
"""

import subprocess
import heapq
from prettytable import PrettyTable
import html
import re
from dao.stocksDAO import StocksDAO
from model.stock import Stock
from model.valuation import Valuation
from enums.rules import Rules
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from libs.googleFinance import GoogleFinance

def pupulating_list_stocks():
    
    list_dict = StocksDAO().list_dict_stock()
    list_stocks = []
    for dict in list_dict:
        stock = Stock(dict['Ticker'], 
                      dict['price_now'], 
                      dict['price_min'], 
                      dict['price_max'], 
                      dict['pTarget'], 
                      dict['payout'])
        list_stocks.append(stock)
    
    return list_stocks    

def get_data_api_yahoo():
    subprocess.getoutput('java -jar libs/yahooFinance.jar')

def get_data_google():
    subprocess.getoutput('python libs/googleFinance.py')

def rule_indicator(indicator):
    if indicator.find('VPATrue') != -1:
        return True
    if indicator.find('D.Y') != -1 and float(indicator.replace('D.Y','')) >= Rules.D_Y.value:
        return True
    if indicator.find('P/L') != -1 and float(indicator.replace('P/L','')) <= Rules.P_L.value:
        return True
    if indicator.find('P/VP') != -1 and float(indicator.replace('P/VP','')) <= Rules.P_VP.value:
        return True
    if indicator.find('P/A') != -1 and float(indicator.replace('P/A','')) <= Rules.P_A.value:
        return True
    if indicator.find('DL/PL') != -1 and float(indicator.replace('DL/PL','')) <= Rules.DL_PL.value:
        return True
    if indicator.find('DL/EBITDA') != -1 and float(indicator.replace('DL/EBITDA','')) <= Rules.DL_EBITDA.value:
        return True
    if indicator.find('LQ') != -1 and float(indicator.replace('LQ','')) >= Rules.L_Q.value:
        return True
    if indicator.find('M.EBIT') != -1 and float(indicator.replace('M.EBIT','')) >= Rules.M_EBIT.value:
        return True
    if indicator.find('M.L') != -1 and float(indicator.replace('M.L','')) >= Rules.M_L.value:
        return True
    if indicator.find('ROE') != -1 and float(indicator.replace('ROE','')) >= Rules.ROE.value:
        return True
    if indicator.find('ROIC') != -1 and float(indicator.replace('ROIC','')) >= Rules.ROIC.value:
        return True
    if indicator.find('CAGR.R') != -1 and float(indicator.replace('CAGR.R','')) >= Rules.CAGR_R.value:
        return True
    if indicator.find('CAGR.L') != -1 and float(indicator.replace('CAGR.L','')) >= Rules.CAGR_L.value:
        return True
    return False

def change_table(table, changes, indicator):
    for row in changes:
        try:
            if rule_indicator(row):
                color = '#228B22'
                table = re.sub('<td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">{}</td>'.format(row), '<td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top" bgcolor="{}">{}</td>'.format(color, row.replace(indicator,'')), table)
            else:
                table = re.sub('<td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">{}</td>'.format(row), '<td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">{}</td>'.format(row.replace(indicator,'')), table)
        except ValueError:
            table = re.sub('<td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">{}</td>'.format(row), '<td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">{}</td>'.format(row.replace(indicator,'')), table)
            continue
    return table

def calc_predict_gain(pNow,dy,pTarget):
    try:
        pNow = float(pNow)
        dy = float(dy)
        pTarget = float(pTarget.replace('*',''))

        price_max = pTarget * (1 + (dy/100))
        pGain = round(((price_max - pNow)/pNow)*100,2)
        if pGain > 0:
            return str(pGain)
        return '-'
    except ValueError:
        return '-'

def main():
    
    #get_data_api_yahoo()
    #get_data_google()
    google = GoogleFinance()
    google.run()
    
    list_stocks = pupulating_list_stocks()

    coll = []
    for stock in list_stocks:
        
        value_min = stock.get_min_value_in_six_month()
        value_max = stock.get_max_value_in_six_month()

        try:
            value_now = stock.get_price_stock_now()
        except ValueError:
            continue
        
        pct_now_min = round(value_now/value_min,2)

        if pct_now_min <= 0:
            continue
        
        if pct_now_min <= 11:
            try:
                vl = Valuation(stock.ticker, 'files/all_indicators.json')
                dic_valuation = vl.get_dict_indicators()
            except IndexError:
                continue
            
            dic_stock ={'Ticker':    stock.ticker,
                        'now': value_now,
                        'min': value_min,
                        'max': value_max,
                        'pTarget': stock.get_price_target(),
                        'payout' : stock.get_payout(),
                        'now/min': pct_now_min,
                        'D.AVG.LQ': dic_valuation['D.AVG.LQ'],
                        'VPA' : dic_valuation['VPA'],
                        'D.Y': dic_valuation['D.Y'],
                        'P/L': dic_valuation['P/L'],
                        'P/VP': dic_valuation['P/VP'],
                        'P/A': dic_valuation['P/A'],
                        'DL/PL': dic_valuation['DL/PL'],
                        'DL/EBITDA': dic_valuation['DL/EBITDA'],
                        'LQ': dic_valuation['LQ'],
                        'M.EBIT': dic_valuation['M.EBIT'],
                        'M.L':    dic_valuation['M.L'],
                        'ROE':    dic_valuation['ROE'],
                        'ROIC':   dic_valuation['ROIC'],
                        'CAGR.R':   dic_valuation['CAGR.R'],
                        'CAGR.L':   dic_valuation['CAGR.L'],
                        'Rank' :    dic_valuation['Rank'],
                        'flagVPA':  dic_valuation['flagVPA']
                    }
            coll.append(dic_stock)

    list_dic_stocks =  heapq.nsmallest(len(coll), coll, key=lambda s: s['now/min'])

    changes_vpa =       []
    changes_dy =        []
    changes_pl =        []
    changes_pvp =       []
    changes_pa =        []
    changes_dlpl =      []
    changes_dlebitda =  []
    changes_lq =        []
    changes_mebit =     []
    changes_ml =        []
    changes_roe =       []
    changes_roic =      []
    changes_cagrr =     []
    changes_cagrl =     []

    myTable = PrettyTable(["ID","Ticker", "pNow", "pTarget","pGain%", "pMin", "pMax", "pNow/pMin","D.AVG.LQ(M)","Ranking","Payout%","VPA", "D.Y%", "P/L", "P/VP", "P/A", "DL/PL", "DL/EBITDA", "LQ", "M.EBIT%", "M.L%", "ROE%", "ROIC%", "CAGR.R%", "CAGR.L%"])
    myTable.align["Ticker"] = "l"

    id = 1
    for dic_stock in list_dic_stocks:

        # if float(dic_stock['Rank']) < 9:
        #     continue

        if float(dic_stock['min']) == -1:
            continue
        
        try:
            if float(dic_stock['P/L']) <= 0:
                continue
        except ValueError:
            pass
        
        try:
            if float(dic_stock['D.AVG.LQ']) < 0.2:
                continue
        except ValueError:
            #pass
            continue

        try:
            pTarget = str(dic_stock['pTarget'])
            payout = dic_stock['payout'] 
            
            if float(dic_stock['now']) <= float(pTarget):
                pTarget+='*'
            if float(dic_stock['now']) <= float(dic_stock['VPA']):
                pTarget+='*'
            if dic_stock['pTarget'] == 0.0:
                pTarget = '-'
            if  dic_stock['payout'] == 0:
                payout  = '-'
                
        except ValueError:
            pTarget = '-'
        except ZeroDivisionError:
            pTarget = '-'
        
        changes_vpa.extend([str(dic_stock['VPA']) + 'VPA' + str(dic_stock['flagVPA'])])
        changes_dy.extend([str(dic_stock['D.Y']) + 'D.Y'])
        changes_pl.extend([str(dic_stock['P/L'])+'P/L'])
        changes_pvp.extend([str(dic_stock['P/VP'])+'P/VP'])
        changes_pa.extend([str(dic_stock['P/A'])+'P/A'])
        changes_dlpl.extend([str(dic_stock['DL/PL'])+'DL/PL'])
        changes_dlebitda.extend([str(dic_stock['DL/EBITDA'])+'DL/EBITDA'])
        changes_lq.extend([str(dic_stock['LQ'])+'LQ'])
        changes_mebit.extend([str(dic_stock['M.EBIT'])+'M.EBIT'])
        changes_ml.extend([str(dic_stock['M.L'])+'M.L'])
        changes_roe.extend([str(dic_stock['ROE'])+'ROE'])
        changes_roic.extend([str(dic_stock['ROIC'])+'ROIC'])
        changes_cagrr.extend([str(dic_stock['CAGR.R'])+'CAGR.R'])
        changes_cagrl.extend([str(dic_stock['CAGR.L'])+'CAGR.L'])

        myTable.add_row([
            id, 
            dic_stock['Ticker'], 
            dic_stock['now'],
            pTarget,
            calc_predict_gain(dic_stock['now'], dic_stock['D.Y'], pTarget),  
            dic_stock['min'], 
            dic_stock['max'], 
            dic_stock['now/min'],
            str(dic_stock['D.AVG.LQ']),
            str(dic_stock['Rank']),
            payout,
            str(dic_stock['VPA'])+'VPA'+ str(dic_stock['flagVPA']),
            str(dic_stock['D.Y'])+'D.Y',
            str(dic_stock['P/L'])+'P/L', 
            str(dic_stock['P/VP'])+'P/VP', 
            str(dic_stock['P/A'])+'P/A', 
            str(dic_stock['DL/PL'])+'DL/PL',
            str(dic_stock['DL/EBITDA'])+'DL/EBITDA', 
            str(dic_stock['LQ'])+'LQ', 
            str(dic_stock['M.EBIT'])+'M.EBIT',
            str(dic_stock['M.L'])+'M.L', 
            str(dic_stock['ROE'])+'ROE', 
            str(dic_stock['ROIC'])+'ROIC',
            str(dic_stock['CAGR.R'])+'CAGR.R', 
            str(dic_stock['CAGR.L'])+'CAGR.L', 
        ])
        
        id += 1

    out_table = myTable.get_html_string(attributes = {"class": "table"},format=True)
    out_table = html.unescape(out_table)
    out_table = change_table(out_table, changes_vpa, 'VPATrue')
    out_table = change_table(out_table, changes_vpa, 'VPAFalse')
    out_table = change_table(out_table, changes_dy, 'D.Y')
    out_table = change_table(out_table, changes_pl, 'P/L')
    out_table = change_table(out_table, changes_pvp, 'P/VP')
    out_table = change_table(out_table, changes_pa, 'P/A')
    out_table = change_table(out_table, changes_dlpl, 'DL/PL')
    out_table = change_table(out_table, changes_dlebitda, 'DL/EBITDA')
    out_table = change_table(out_table, changes_lq, 'LQ')
    out_table = change_table(out_table, changes_mebit, 'M.EBIT')
    out_table = change_table(out_table, changes_ml, 'M.L')
    out_table = change_table(out_table, changes_roe, 'ROE')
    out_table = change_table(out_table, changes_roic, 'ROIC')
    out_table = change_table(out_table, changes_cagrr, 'CAGR.R')
    out_table = change_table(out_table, changes_cagrl, 'CAGR.L')

    print(out_table)

if __name__ == '__main__':
    main()