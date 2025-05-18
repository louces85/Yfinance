from shutil import ExecError
import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
#print(SCRIPT_DIR)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
#print(sys.path)
from jdbc.connection_factory import Connection_Factory
from model.valuation import Valuation
from tqdm import tqdm

class ValuationDAO():

    def __init__(self, ticker):
        self.ticker = ticker
        self.vl = Valuation(self.ticker, 'files/all_indicators.json')
    
    def update_price_target(self):
        conn = Connection_Factory().connection()
        cur = conn.cursor()
        p_target = self.vl.get_price_target()
        cur.execute("update valuation set price_target={} where ticker like '{}';".format(p_target, self.ticker))
        cur.execute("select price_now from price where ticker like '{}';".format(self.ticker))
        
        price_targets_strings = []
        #price_target = self.vl.get_price_target()
        list_div_year = self.vl.list_price_target_year[::-1]
        
        for dicionario in list_div_year:
            price_target_string = f"{round(dicionario['price_parcial_years'],2)}"
            price_targets_strings.append(price_target_string)

        # Concatena os strings usando ":"
        prices_target = ":".join(price_targets_strings)


        price_now = cur.fetchall()[0][0]
        dict_indicadores = self.vl.get_dict_indicators()

        vpa = dict_indicadores['VPA']
        liquides_diaria = dict_indicadores['D.AVG.LQ']
        rank = dict_indicadores['Rank']
        p_l = dict_indicadores['P/L']
        
            
        if(price_now == 0 or len(list_div_year)==0 or p_l <= 0.0):
            return

#               Tiker,Rank,Preco_atual,vpa,pl,ganho,Preco_target_2023,Preco_target_2022,Preco_target_2021,Preco_target_2020,Preco_target_2019,liquides_diaria
        print(f"{self.ticker}:{rank}:{price_now}:{vpa}:{p_l}:0.0:{prices_target}:{liquides_diaria}")
            
        
        cur.close()

        conn.commit()
        conn.close    

    def update_payout(self):
        conn = Connection_Factory().connection()
        
        cur = conn.cursor()
        cur.execute("update valuation set payout={} where ticker like '{}';".format(self.vl.get_payout(), self.ticker))
        cur.close()

        conn.commit()
        conn.close

    def get_price_target(self):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        cur.execute("select price_target from valuation where ticker like '{}';".format(self.ticker))

        price_target = cur.fetchall()[0][0]
        cur.close()

        conn.commit()
        conn.close
        return price_target

    def get_payout(self):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        cur.execute("select payout from valuation where ticker like '{}';".format(self.ticker))

        paytout = cur.fetchall()[0][0]
        cur.close()

        conn.commit()
        conn.close
        return paytout

    def update_all(self):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        query = "select ticker from history where net_income = true;"
        cur.execute(query)

        list_tuple = cur.fetchall()
        cur.close()

        conn.commit()
        conn.close
        
        #for t in tqdm(list_tuple):
        for t in list_tuple:
            vlDAO = ValuationDAO(t[0])
            vlDAO.update_payout()
            vlDAO.update_price_target()

vlDAO = ValuationDAO('')
print(vlDAO.update_all())