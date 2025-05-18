import yfinance as yf
import warnings
from pandas.errors import SettingWithCopyWarning
import sys
import os
from prettytable import PrettyTable
from tqdm import tqdm
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from jdbc.connection_factory import Connection_Factory
from model.history_prices import get_all_stocks
from dao.stocksDAO import StocksDAO
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

class Prices:
    def __init__(self, ticker, historical_data):
        self.ticker = ticker.replace(".SA", "")  # Remove .SA for database queries
        self.historical_data = historical_data
        self.last_week_prices = self.get_last_week_prices()
        self.ptarget = self.get_ptarget()

    def get_ptarget(self):
        """Get price target from database"""
        try:
            stocks_dao = StocksDAO()
            stocks_list = stocks_dao.list_dict_stock()
            for stock in stocks_list:
                if stock['Ticker'] == self.ticker:
                    return stock['pTarget']
            return None
        except Exception as e:
            print(f"Error getting ptarget for {self.ticker}: {e}")
            return None

    def get_last_week_prices(self):
        try:
            # Get historical data for the last 30 days
            prices = self.historical_data['Close'].dropna()
            if prices.empty:
                return "No price data available"
            return prices
        except Exception as e:
            if "delisted" in str(e).lower():
                return f"Stock {self.ticker} possibly delisted"
            return f"Error: {str(e)}"

    def get_average_last_week_price(self):
        prices = self.last_week_prices
        if isinstance(prices, str):
            return prices
        return prices.mean()

    def get_last_valid_price(self):
        prices = self.last_week_prices
        if isinstance(prices, str):
            return prices
        
        # Find the last non-zero price
        try:
            non_zero_prices = prices[prices != 0]
            if non_zero_prices.empty:
                return "No valid non-zero price found in the last week"
            return non_zero_prices.iloc[-1]
        except Exception as e:
            return f"Error getting last valid price: {str(e)}"

    def get_last_valid_price_percentage(self):
        last_valid_price = self.get_last_valid_price()
        if isinstance(last_valid_price, str):
            return last_valid_price
        average_price = self.get_average_last_week_price()    
        if average_price == 0:
            return 0
        return round((last_valid_price - average_price) * 100 / average_price, 2)

if __name__ == "__main__":
    list_all_ticker = get_all_stocks()
    
    # Create lists to store the data
    table_data = []
    
    for ticker in tqdm(list_all_ticker[:40], desc="Processing stocks"):
        prices = Prices(ticker + ".SA")
        last_week = prices.last_week_prices
        
        if isinstance(last_week, str):
            if "delisted" in last_week.lower():
                continue
        else:
            average = prices.get_average_last_week_price()
            last_valid = prices.get_last_valid_price()
            if(last_valid == "No valid non-zero price found in the last week"):
                continue
            if(average < 1):  # Skip stocks with very low average price
                continue
            percentage = prices.get_last_valid_price_percentage()
            
            # Convert price and percentage to float for proper sorting
            try:
                if isinstance(last_valid, (int, float)):
                    numeric_price = float(last_valid)
                else:
                    numeric_price = float(str(last_valid).replace(',', ''))
                if numeric_price > 0:  # Only add if price is greater than 0
                    # Convert percentage to float
                    numeric_percentage = float(percentage)
                    numeric_average = float(average) if isinstance(average, (int, float)) else float(str(average).replace(',', ''))
                    table_data.append([ticker, numeric_price, numeric_average, last_valid, numeric_percentage])
            except:
                continue
    
    # Create and print table for top 10 highest percentage variations
    high_price_table = PrettyTable(["Ticker", "Last Price", "Average Price", "Last Valid Price", "Price %"])
    high_price_table.align["Ticker"] = "l"
    print("\nTop 10 Highest Price % Variation:")
    # Sort by percentage (fifth column) in descending order
    table_data.sort(key=lambda x: x[4], reverse=True)
    for row in table_data[:10]:
        high_price_table.add_row([
            row[0], 
            format(row[1], '.2f'), 
            format(row[2], '.2f'), 
            str(row[3]), 
            format(row[4], '.2f') + "%"
        ])
    print(high_price_table)
    
    # Create and print table for top 10 lowest percentage variations
    low_price_table = PrettyTable(["Ticker", "Last Price", "Average Price", "Last Valid Price", "Price %"])
    low_price_table.align["Ticker"] = "l"
    print("\nTop 10 Lowest Price % Variation:")
    # Sort by percentage in ascending order (most negative first)
    table_data.sort(key=lambda x: x[4])
    for row in table_data[:10]:
        low_price_table.add_row([
            row[0], 
            format(row[1], '.2f'), 
            format(row[2], '.2f'), 
            str(row[3]), 
            format(row[4], '.2f') + "%"
        ])
    print(low_price_table)
    
    # Print total number of stocks analyzed
    print(f"\nTotal stocks analyzed: {len(table_data)}") 