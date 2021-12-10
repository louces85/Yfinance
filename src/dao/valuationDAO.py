import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from jdbc.connection_factory import Connection_Factory
from model.valuation import Valuation

class ValuationDAO():

    def __init__(self, ticker):
        self.ticker = ticker
        self.vl = Valuation(self.ticker, 'files/all_indicators.json')
    
    def update_price_target(self):
        conn = Connection_Factory().connection()
        
        cur = conn.cursor()
        cur.execute("update valuation set price_target={} where ticker like '{}';".format(self.vl.get_price_target(), self.ticker))
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
        
        for t in list_tuple:
            vlDAO = ValuationDAO(t[0])
            vlDAO.update_payout()
            vlDAO.update_price_target()

vlDAO = ValuationDAO('')
print(vlDAO.update_all())