import yfinance as yf
import warnings
#from pandas.core.common import SettingWithCopyWarning
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
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

class Volume:

    def __init__(self, ticker, historical_data):
        self.ticker = ticker
        self.historical_data = historical_data
        self.last_week_volume = self.get_last_week_volume()

    def get_last_week_volume(self):
        try:
            # Get historical data for the last 30 days
            # Remove NaN values and check if we have data
            volumes = self.historical_data['Volume'].dropna()
            if volumes.empty:
                return "No volume data available"
            return volumes
        except Exception as e:
            if "delisted" in str(e).lower():
                return f"Stock {self.ticker} possibly delisted"
            return f"Error: {str(e)}"
    
    def get_average_last_week_volume(self):
        volumes = self.last_week_volume
        if isinstance(volumes, str):
            return volumes
        return volumes.mean()
    
    def get_last_valid_volume(self):
        volumes = self.last_week_volume
        if isinstance(volumes, str):
            return volumes
        
        # Find the last non-zero volume
        try:
            non_zero_volumes = volumes[volumes != 0]
            if non_zero_volumes.empty:
                return "No valid non-zero volume found in the last week"
            return non_zero_volumes.iloc[-1]
        except Exception as e:
            return f"Error getting last valid volume: {str(e)}"
    
    def get_last_valid_volume_percentage(self):
        last_valid_volume = self.get_last_valid_volume()
        if isinstance(last_valid_volume, str):
            return last_valid_volume
        average_volume = self.get_average_last_week_volume()    
        if average_volume == 0:
            return 0
        return round((last_valid_volume - average_volume) * 100 / average_volume, 2)    

if __name__ == "__main__":
    list_all_ticker = get_all_stocks()
    
    # Create lists to store the data
    table_data = []
    
    #do ultil 40 stocks
    for ticker in tqdm(list_all_ticker[:40], desc="Processing stocks"):
        volume = Volume(ticker + ".SA")
        last_week = volume.last_week_volume
        
        if isinstance(last_week, str):
            if "delisted" in last_week.lower():
                continue
        else:
            average = volume.get_average_last_week_volume()
            last_valid = volume.get_last_valid_volume()
            if(last_valid == "No valid non-zero volume found in the last week"):
                continue
            if(average < 1000000):
                continue
            percentage = volume.get_last_valid_volume_percentage()
            
            # Convert volume and percentage to float for proper sorting
            try:
                if isinstance(last_valid, (int, float)):
                    numeric_volume = float(last_valid)
                else:
                    numeric_volume = float(str(last_valid).replace(',', ''))
                if numeric_volume > 0:  # Only add if volume is greater than 0
                    # Convert percentage to float
                    numeric_percentage = float(percentage)
                    numeric_average = float(average) if isinstance(average, (int, float)) else float(str(average).replace(',', ''))
                    table_data.append([ticker, numeric_volume, numeric_average, last_valid, numeric_percentage])
            except:
                continue
    
    # Create and print table for top 10 highest percentage variations
    high_volume_table = PrettyTable(["Ticker", "Last Volume", "Average Volume", "Last Valid Volume", "Volume %"])
    high_volume_table.align["Ticker"] = "l"
    print("\nTop 10 Highest Volume % Variation:")
    # Sort by percentage (fifth column) in descending order
    table_data.sort(key=lambda x: x[4], reverse=True)
    for row in table_data[:10]:
        high_volume_table.add_row([
            row[0], 
            format(row[1], '.0f'), 
            format(row[2], '.2f'), 
            str(row[3]), 
            format(row[4], '.2f') + "%"
        ])
    print(high_volume_table)
    
    # Create and print table for top 10 lowest percentage variations
    low_volume_table = PrettyTable(["Ticker", "Last Volume", "Average Volume", "Last Valid Volume", "Volume %"])
    low_volume_table.align["Ticker"] = "l"
    print("\nTop 10 Lowest Volume % Variation:")
    # Sort by percentage in ascending order (most negative first)
    table_data.sort(key=lambda x: x[4])
    for row in table_data[:10]:  # Get first 10 after sorting in ascending order
        low_volume_table.add_row([
            row[0], 
            format(row[1], '.0f'), 
            format(row[2], '.2f'), 
            str(row[3]), 
            format(row[4], '.2f') + "%"
        ])
    print(low_volume_table)
    
    # Print total number of stocks analyzed
    print(f"\nTotal stocks analyzed: {len(table_data)}")
    