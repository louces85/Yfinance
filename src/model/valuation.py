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
        self.list_price_target_year = []

    def get_list_stoks(self):
        with open(self.name_json_file, encoding='utf-8') as json_file:
            list_dict_stoks = json.load(json_file)
            return list_dict_stoks

    def get_dict_indicators(self):
        list = self.get_list_stoks() 
        dict_json = {}
        
        for l in list:
            #print(l)
            if l['ticker'] == self.ticker:
                dict_json = l
                break
        
        dict_stock = {
                'Ticker':    dict_json.get('ticker', '-'),
                'D.Y':       dict_json.get('dy', '-'),
                'P/L':       dict_json.get('p_l', '-'),
                'P/VP':      dict_json.get('p_vp', '-'),
                'VPA':       dict_json.get('vpa', '-'),
                'P/A':       dict_json.get('passivo_ativo', '-'),
                'DL/PL':     dict_json.get('dividaliquidapatrimonioliquido', '-'),
                'DL/EBITDA': dict_json.get('dividaliquidaebit', '-'),
                'LQ':        dict_json.get('liquidezcorrente', '-'),    
                'M.EBIT':    dict_json.get('margemebit', '-'),
                'M.L':       dict_json.get('margemliquida', '-'),
                'ROE':       dict_json.get('roe', '-'),
                'ROIC':      dict_json.get('roic', '-'),
                'CAGR.R':    dict_json.get('receitas_cagr5', '-'),
                'CAGR.L':    dict_json.get('lucros_cagr5', '-'),
                'D.AVG.LQ':  dict_json.get('liquidezmediadiaria', '-'),   
                'Rank' :     0,
                'flagVPA':   False
        }
        
        try:
            dict_stock['D.AVG.LQ'] = round(float(dict_stock['D.AVG.LQ'])/1000000,2)
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
        except Exception as e:
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
        
        #format_str = "curl -s  https://statusinvest.com.br/acao/payoutresult?code=" + self.ticker.strip().lower() + " | grep 'actual' | awk -F ':' '{print $3}' | awk -F ',' '{print $1}'"
        format_str =  'curl -s --user-agent "Chrome/79" "https://statusinvest.com.br/acao/payoutresult?code="' + self.ticker.strip().lower() + " | grep 'actual' | awk -F ':' '{print $3}' | awk -F ',' '{print $1}'"
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

        for y in range(5):
            year = (datetime.datetime.now()-relativedelta(years=(y+1))).strftime("%Y")
            years.append(year)

        list_erros = [
            "ALSC3.SA",
            "ANDG3B.SA",
            "ANDG4B.SA",
            "APTI3.SA",
            "APTI4.SA",
            "BBML3.SA", "BEEF11.SA", "BFRE12.SA", "BIDI11.SA", "BIDI3.SA", "BIDI4.SA", 
            "BLUT3.SA", "BLUT4.SA", "BOAS3.SA", "BPAR3.SA", "BPAT33.SA", "BRBI3.SA", 
            "BRBI4.SA", "BRIN3.SA", "BRML3.SA", "BRQB3.SA", "BSEV3.SA", "CATA3.SA", 
            "CATA4.SA", "CCXC3.SA", "CEEB6.SA", "CEPE3.SA", "CEPE5.SA", "CEPE6.SA", 
            "CESP3.SA", "CESP5.SA", "CESP6.SA", "CMSA3.SA", "CMSA4.SA", "CNSY3.SA", 
            "CPRE3.SA", "CTCA3.SA", "DMMO11.SA", "DMMO3.SA", "DTCY4.SA", "EEEL4.SA", 
            "ELEK3.SA", "ELEK4.SA", "ELPL3.SA", "CAMB4.SA", "ENMA3B.SA", "ENMA6B.SA", 
            "FLEX3.SA", "FTRT3B.SA", "GBIO33.SA", "GETT11.SA", "GETT3.SA", "GETT4.SA", 
            "GUAR4.SA", "HGTX3.SA", "IDVL3.SA", "IDVL4.SA", "IGTA3.SA", "INNT3.SA", 
            "ITEC3.SA", "LAME3.SA", "LAME4.SA", "LCAM3.SA", "LINX3.SA", "ENBR3.SA", 
            "LTEL3B.SA", "MAGG3.SA", "MMXM3.SA", "MODL11.SA", "MODL3.SA", "MODL4.SA", 
            "MOSI3.SA", "MPLU3.SA", "MSRO3.SA", "MTIG4.SA", "NAFG3.SA", "NAFG4.SA", 
            "NRTQ3.SA", "OMGE3.SA", "PARD3.SA", "PCAR4.SA", "PNVL4.SA", "PTCA11.SA", 
            "PTCA3.SA", "QGEP3.SA", "QUSW3.SA", "QVQP3B.SA", "RANI4.SA", "RLOG3.SA", 
            "SEDU3.SA", "SMLS3.SA", "SPRI3.SA", "SPRI5.SA", "SPRI6.SA", "SPRT3B.SA", 
            "SQIA3.SA", "STKF3.SA", "STTR3.SA", "SULA11.SA", "SULA3.SA", "SULA4.SA", 
            "TCNO3.SA", "TCNO4.SA", "TESA3.SA", "TIET11.SA", "TIET3.SA", "TIET4.SA", 
            "TOYB3.SA", "TOYB4.SA", "TRPN3.SA", "FNCN3.SA", "GNDI3.SA", "POWE3.SA", 
            "VIVT4.SA", "TICKER.SA", "CALI4.SA", "EEEL3.SA"
        ]
        
        if f"{self.ticker}.SA" in list_erros:
            #print(self.ticker)
            return


        msft = yfinance.Ticker(self.ticker + '.SA')
    
        history_dividends = msft.dividends
        sum_dividends = 0
        count_years   = 0

        #print(history_dividends)
    
        try:
            sum_div_parcial_years = 0
            for year in years:
                #print(year)
                flag = False
                #print(history_dividends.keys())
                sum_div_year = 0
                
                for k in history_dividends.keys():
                    
                    if(str(k).find(year) == 0):
                        flag = True
                        #print(f"{k}:{history_dividends.get(k)}")
                        sum_dividends += float(history_dividends.get(k))
                        sum_div_year += float(history_dividends.get(k))
                
                if flag == True:
                    #print(f"Total: {k} :{sdy}")
                    #print(f"Total:{year}:{sum_div_year}")
                    count_years += 1
                
                #print(f"Total: {year} :{sum_div_year}")
                
                # price_target = (sum_div_year/count_years)/0.06
                sum_div_parcial_years += sum_div_year
                dict_temp = {
                    'ticker': self.ticker,
                    'year':year,
                    'sum_div_parcial_years' : sum_div_parcial_years,
                    'price_parcial_years' : sum_div_parcial_years/count_years/0.06
                }



                # for s_y in self.list_price_target_year:
                #     dict_temp['price_target'] += s_y

                self.list_price_target_year.append(dict_temp)

            if(count_years == 0):
                #print(f"{self.ticker}\t--\t--\t--") 
                return
            #sum_total = sum_dividends/count_years
            #price = float(sum_total/0.06)

            #print("")

            temp = float(sum_dividends/count_years/0.06)
            #print(f"{self.ticker} {round(price,2)}")
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