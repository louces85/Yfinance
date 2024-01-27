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

class GoogleFinance:

    def __init__(self):
        pass


    def getPriceStock(self,ticker):
        
        try:
            url = "https://www.google.com/finance/quote/"+ticker+":BVMF"
            #print(url)

            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            price_element = soup.find("div", class_="YMlKec fxKbKc")
            price = price_element.text.split("R$")

            return price[1]    
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