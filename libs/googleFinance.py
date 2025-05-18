import sys
import os
from traceback import print_tb
import warnings
#from pandas.core.common import SettingWithCopyWarning
from pandas.errors import SettingWithCopyWarning
import requests
from bs4 import BeautifulSoup
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from src.jdbc.connection_factory import Connection_Factory
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
import re

class GoogleFinance:

    def __init__(self):
        pass


    def getPriceStock(self,ticker):
        
        try:
            url = "https://www.google.com/finance/quote/"+ticker+":BVMF"
            #print(url)

            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for any bad response status
            
            # Create a BeautifulSoup object only for the required part of the HTML
            price_html = response.text.split("YMlKec fxKbKc")[1]
            soup = BeautifulSoup(price_html, "html.parser")
            
            
            price_text = soup.text
            price_match = re.search(r'(\d+\.\d+)', price_text)
            if price_match:
                price = price_match.group(0)
                return float(price)
            else:
                return "Value not found"

        except Exception as e:
            pass
            #print(e)
            

    def listStocks(self):
        conn = Connection_Factory().connection() 

        cur = conn.cursor()
        cur.execute("select * from history where net_income = true;")

        list = cur.fetchall()
        cur.close()

        conn.commit()
        conn.close

        list_stocks = []
        for stock in list:
            list_stocks.append(stock[1])
        
        return list_stocks

    def uptate_price_stock(self, ticker, price_now):
        conn = Connection_Factory().connection()
        
        cur = conn.cursor()
        cur.execute("update price set price_now={} where ticker like '{}';".format(price_now, ticker))
        cur.close()

        conn.commit()
        conn.close

    def run(self):

        for ticker in self.listStocks():
            
            price_now = self.getPriceStock(ticker)
            
            if price_now is None:
                continue
            
            self.uptate_price_stock(ticker, price_now)

if __name__ == '__main__':

    google = GoogleFinance()
    google.run()