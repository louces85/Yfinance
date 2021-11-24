import subprocess

class Stock:

    def __init__(self, ticker):
        self.ticker = ticker
    
    def get_price_stock_now(self):
        format_str = "cat files/prices_stocks | grep '"+self.ticker+"'"  + " | awk '{print$7}' | awk -F ',' '{print$1}' | head -n 1"
        return float(subprocess.getoutput(format_str).strip())
    
    def get_max_value_in_six_month(self):
        format_str = "cat files/history_6mo_results_net_income | grep '"+self.ticker+"'"  + " | awk '{print$3}' | head -n 1"
        return float(subprocess.getoutput(format_str).strip())
    
    def get_min_value_in_six_month(self):
        format_str = "cat files/history_6mo_results_net_income | grep '"+self.ticker+"'"  + " | awk '{print$(NF-3)}' | head -n 1"
        return float(subprocess.getoutput(format_str).strip())
    
    def is_net_income_positive_in_four_years(self):
        format_str = "cat files/history_6mo_results_net_income | grep '"+self.ticker+"'"  + " | awk '{print$NF}' | head -n 1"
        return subprocess.getoutput(format_str).strip()
    

#stock = Stock('BBSE3')
#print(stock.get_price_stock_now())
#print(stock.get_max_value_in_six_month())
#print(stock.get_min_value_in_six_month())
#print(stock.is_net_income_positive_in_four_years())

