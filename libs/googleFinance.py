import sys
import os
from traceback import print_tb
import warnings
#from pandas.core.common import SettingWithCopyWarning
from pandas.errors import SettingWithCopyWarning
import requests, time
import httpx
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
            #print("Testando:", url)
            headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                    "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-form-factors": '"Desktop"',
            "sec-ch-ua-full-version": '"134.0.6998.88"',
            "sec-ch-ua-full-version-list": '"Chromium";v="134.0.6998.88", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.88"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Linux"',
            "sec-ch-ua-platform-version": '"5.15.0"',
            "sec-ch-ua-wow64": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "same-site",
            "x-client-data": "CIe2yQEIprbJAQipncoBCJXoygEIlqHLAQiHoM0BGOHizgE=",
            "connection": "keep-alive",
            }
            timeout = httpx.Timeout(2.0, read=5.0)
            with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True, http2=True) as client:
                #start = time.time()
                r = client.get(url)
                #elapsed = time.time() - start

                #print("Status:", r.status_code)
                #print("Tempo:", round(elapsed, 2), "s")
                #print("Len:", len(r.text))
                # ver redirects:
                #print("Redirect history:", [resp.status_code for resp in r.history])
           
            #response = requests.get(url, headers=headers, timeout=60)
            #response.raise_for_status()  # Raise an exception for any bad response status
            
            # Create a BeautifulSoup object only for the required part of the HTML
                price_html = r.text.split("YMlKec fxKbKc")[1]
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