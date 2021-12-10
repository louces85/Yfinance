import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from jdbc.connection_factory import Connection_Factory

class HistoryDAO:

    def __init__(self, ticker):
        self.ticker  = ticker
        
    def get_max_value_in_six_month(self):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        cur.execute("select price_max from history where ticker like '{}';".format(self.ticker))

        price_max = cur.fetchall()[0][0]
        cur.close()

        conn.commit()
        conn.close
        return price_max

    def get_min_value_in_six_month(self):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        cur.execute("select price_min from history where ticker like '{}';".format(self.ticker))

        price_min = cur.fetchall()[0][0]
        cur.close()

        conn.commit()
        conn.close
        return price_min

    def is_net_income_positive_in_four_years(self):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        cur.execute("select net_income from history where ticker like '{}' and net_income = true;".format(self.ticker))

        flag = cur.fetchall()[0][0]
        cur.close()

        conn.commit()
        conn.close
        return flag

