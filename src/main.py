"""
-----------------------------------------------------------------------------
@copyright 2021 Fabiano Louzada
@doc Analyze B3 stocks List
@author Fabiano Louzada Cesario <fabiano.cesario.k@gmail.com>
@yfinance 1.0
-----------------------------------------------------------------------------
"""

from enum import Flag
import subprocess
import heapq
import time
from prettytable import PrettyTable
import html
import re

file_in  = open('files/stocks_file', 'r')

def pupulating_list_stocks(file_in):
    list_stk = []
    file_out = open('files/stocks_file_incomes_positive', 'w')
    for stock in file_in:
        
        if(is_net_income_positive_in_four_years(stock.strip())=='True'):
            list_stk.append(stock.strip()+'.SA')
            file_out.write(stock.strip()+'\n')
            file_out.flush()
    
    file_out.close()
    return list_stk

def get_data_api_yahoo():
    subprocess.getoutput('java -jar libs/yahooFinance.jar ~/Documents/Yfinance/files/stocks_file_incomes_positive > files/prices_stocks')
    
def get_price_stock_now(ticker):
    format_str = "cat ~/Documents/Yfinance/files/prices_stocks | grep '"+ticker+"'"  + " | awk '{print$7}' | awk -F ',' '{print$1}'"
    return float(subprocess.getoutput(format_str).strip())

def get_max_value_in_six_month(ticker):
    format_str = "cat ~/Documents/Yfinance/files/history_6mo_results_net_income | grep '"+ticker+"'"  + " | awk '{print$3}'"
    return float(subprocess.getoutput(format_str).strip())

def get_min_value_in_six_month(ticker):
    format_str = "cat ~/Documents/Yfinance/files/history_6mo_results_net_income | grep '"+ticker+"'"  + " | awk '{print$(NF-3)}'"
    return float(subprocess.getoutput(format_str).strip())

def is_net_income_positive_in_four_years(ticker):
    format_str = "cat ~/Documents/Yfinance/files/history_6mo_results_net_income | grep '"+ticker+"'"  + " | awk '{print$NF}'"
    return subprocess.getoutput(format_str).strip()

def get_valuation(ticker):
    
    format_str = "curl -s https://statusinvest.com.br/acoes/" + ticker.strip().lower().replace('.sa','') + " | grep 'value d-block lh-4 fs-4 fw-700' | grep 'value d-block lh-4 fs-4 fw-700' | grep 'class' | awk '{print $NF}' | awk -F '>' '{print $2}' | awk -F '<' '{print $1}'"
    index = subprocess.getoutput(format_str).split('\n')
    
    dic_stok = {
        'Ticker':    ticker.strip().lower(),
        'D.Y':       index[0].replace(',','.').replace('%',''),
        'P/L':       index[1].replace(',','.'),
        'P/VP':      index[3].replace(',','.'),
        'VPA':       index[8].replace(',','.'),
        'P/A':       index[18].replace(',','.'),
        'DL/PL':     index[14].replace(',','.'),
        'DL/EBITDA': index[15].replace(',','.'),
        'LQ':        index[19].replace(',','.'),
        'M.EBIT':    index[22].replace(',','.').replace('%',''),
        'M.L':       index[23].replace(',','.').replace('%',''),
        'ROE':       index[24].replace(',','.').replace('%',''),
        'ROIC':      index[26].replace(',','.').replace('%',''),
        'CAGR.R':    index[28].replace(',','.').replace('%',''),
        'CAGR.L':    index[29].replace(',','.').replace('%',''),
        'Rank' :     0,
        'flagVPA':   False
    }
    
    time.sleep(.3)
    dic_stok['Rank']    = get_rank(dic_stok)[0]
    dic_stok['flagVPA'] = get_rank(dic_stok)[1]
    return dic_stok

def get_rank(dic_stok):
    rank = 0
    flag_vpa = False
    
    try:
        price_now = (get_price_stock_now((dic_stok['Ticker'].upper())))
        if price_now <= float(dic_stok['VPA']):
            flag_vpa = True
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['D.Y']) >= 5:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['P/L']) <= 15:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['P/VP']) <= 1.5:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['DL/PL']) <= 1:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['DL/EBITDA']) <= 3:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['P/A']) <= 1:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['LQ']) >= 1:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['M.EBIT']) >= 10:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['M.L']) >= 10:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['ROE']) >= 10:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['ROIC']) >= 10:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['CAGR.R']) >= 5:
            rank += 1
    except ValueError:
        pass

    try:
        if float(dic_stok['CAGR.L']) >= 5:
            rank += 1
    except ValueError:
        pass

    return rank , flag_vpa

def rule_indicator(indicator):
    if indicator.find('VPATrue') != -1:
        return True
    if indicator.find('D.Y') != -1 and float(indicator.replace('D.Y','')) >= 5:
        return True
    if indicator.find('P/L') != -1 and float(indicator.replace('P/L','')) <= 15:
        return True
    if indicator.find('P/VP') != -1 and float(indicator.replace('P/VP','')) <= 1.5:
        return True
    if indicator.find('P/A') != -1 and float(indicator.replace('P/A','')) <= 1:
        return True
    if indicator.find('DL/PL') != -1 and float(indicator.replace('DL/PL','')) <= 1:
        return True
    if indicator.find('DL/EBITDA') != -1 and float(indicator.replace('DL/EBITDA','')) <= 3:
        return True
    if indicator.find('LQ') != -1 and float(indicator.replace('LQ','')) >= 1:
        return True
    if indicator.find('M.EBIT') != -1 and float(indicator.replace('M.EBIT','')) >= 10:
        return True
    if indicator.find('M.L') != -1 and float(indicator.replace('M.L','')) >= 10:
        return True
    if indicator.find('ROE') != -1 and float(indicator.replace('ROE','')) >= 10:
        return True
    if indicator.find('ROIC') != -1 and float(indicator.replace('ROIC','')) >= 10:
        return True
    if indicator.find('CAGR.R') != -1 and float(indicator.replace('CAGR.R','')) >= 5:
        return True
    if indicator.find('CAGR.L') != -1 and float(indicator.replace('CAGR.L','')) >= 5:
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

def main():

    get_data_api_yahoo()

    list_stocks = pupulating_list_stocks(file_in)

    coll = []
    for dic_stock in list_stocks:
        value_min = get_min_value_in_six_month(dic_stock)
        value_max = get_max_value_in_six_month(dic_stock)
        try:
            value_now = get_price_stock_now(dic_stock)
        except ValueError:
            continue
        
        pct_now_min = round(value_now/value_min,4)

        if (pct_now_min <= 0):
            continue
        
        try:
            pct_now_max = round((value_max-value_now)*100/value_now,2)
        except ZeroDivisionError:
            continue

        if pct_now_min <= 1.1:
            try:
                dic_valuation = get_valuation(dic_stock)
            except IndexError:
                continue
            
            dic_stock ={'Ticker':    dic_stock.replace('.SA', ''),
                        'now': value_now,
                        'min': value_min,
                        'max': value_max,
                        'now/min': pct_now_min,
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

    myTable = PrettyTable(["ID","Ticker", "pNow", "pMin", "pMax", "pNow/pMin", "VPA", "D.Y%", "P/L", "P/VP", "P/A", "DL/PL", "DL/EBITDA", "LQ", "M.EBIT%", "M.L%", "ROE%", "ROIC%", "CAGR.R%", "CAGR.L%", "R"])
    myTable.align["Ticker"] = "l"

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

    id = 1
    for dic_stock in list_dic_stocks:

        if dic_stock['min'] > 100:
            continue
        
        changes_vpa.extend([dic_stock['VPA']+'VPA' + str(dic_stock['flagVPA'])])
        changes_dy.extend([dic_stock['D.Y']+'D.Y'])
        changes_pl.extend([dic_stock['P/L']+'P/L'])
        changes_pvp.extend([dic_stock['P/VP']+'P/VP'])
        changes_pa.extend([dic_stock['P/A']+'P/A'])
        changes_dlpl.extend([dic_stock['DL/PL']+'DL/PL'])
        changes_dlebitda.extend([dic_stock['DL/EBITDA']+'DL/EBITDA'])
        changes_lq.extend([dic_stock['LQ']+'LQ'])
        changes_mebit.extend([dic_stock['M.EBIT']+'M.EBIT'])
        changes_ml.extend([dic_stock['M.L']+'M.L'])
        changes_roe.extend([dic_stock['ROE']+'ROE'])
        changes_roic.extend([dic_stock['ROIC']+'ROIC'])
        changes_cagrr.extend([dic_stock['CAGR.R']+'CAGR.R'])
        changes_cagrl.extend([dic_stock['CAGR.L']+'CAGR.L'])

        myTable.add_row([
            id, 
            dic_stock['Ticker'], 
            dic_stock['now'], 
            dic_stock['min'], 
            dic_stock['max'], 
            dic_stock['now/min'], 
            dic_stock['VPA']+'VPA'+ str(dic_stock['flagVPA']), 
            dic_stock['D.Y']+'D.Y',
            dic_stock['P/L']+'P/L', 
            dic_stock['P/VP']+'P/VP', 
            dic_stock['P/A']+'P/A', 
            dic_stock['DL/PL']+'DL/PL',
            dic_stock['DL/EBITDA']+'DL/EBITDA', 
            dic_stock['LQ']+'LQ', 
            dic_stock['M.EBIT']+'M.EBIT',
            dic_stock['M.L']+'M.L', 
            dic_stock['ROE']+'ROE', 
            dic_stock['ROIC']+'ROIC',
            dic_stock['CAGR.R']+'CAGR.R', 
            dic_stock['CAGR.L']+'CAGR.L', 
            dic_stock['Rank']
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