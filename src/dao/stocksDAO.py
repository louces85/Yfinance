import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from jdbc.connection_factory import Connection_Factory

class StocksDAO:

    def __init__(self):
        pass

    def list_dict_stock(self):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        query = "select stock.ticker, price.price_now, history.price_min, history.price_max, valuation.price_target, valuation.payout from stock inner join price on stock.ticker = price.ticker inner join history on price.ticker = history.ticker and history.net_income = true inner join valuation on history.ticker = valuation.ticker;"
        cur.execute(query)

        all_stocks = cur.fetchall()
        cur.close()

        conn.commit()
        conn.close
        list = []
        for tuple in all_stocks:
            ticker, price_now , price_min, price_max, pTarget, payout = tuple
            dict_stock = { 'Ticker' : ticker,
                           'price_now' : price_now,
                           'price_min' : price_min,
                           'price_max' : price_max,
                           'pTarget'   : pTarget,
                           'payout'    : payout
            }
            list.append(dict_stock)

        return list

    def get_price(self, ticker):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        query = "select price_now from price where ticker like '{}';".format(ticker)
        cur.execute(query)

        price_now = cur.fetchall()[0][0]
        cur.close()

        conn.commit()
        conn.close
        return price_now