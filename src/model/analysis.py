import yfinance as yf
import warnings
from pandas.errors import SettingWithCopyWarning
import sys
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import plotly.io as pio
from prettytable import PrettyTable
import re

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from model.volume import Volume
from model.prices import Prices
from model.history_prices import get_all_stocks
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

list_delisted = ['APER3', 'APTI3', 'BBML3', 'BFRE11', 'BFRE12', 'BIDI11', 'BIDI3', 'BIDI4', 
                 'BLUT3', 'BLUT4', 'BOAS3', 'BPAT33', 'BPHA3', 'BRBI3', 'BRBI4', 'BRQB3', 
                 'BSEV3', 'CALI4', 'CAMB4', 'AESB3', 'CEEB6', 'CEPE3', 'CEPE5', 'CEPE6', 
                 'CESP3', 'CESP5', 'CESP6', 'CIEL3', 'CMSA3', 'CMSA4', 'CNSY3', 'CPRE3', 
                 'CREM3', 'CSAB3', 'CSAB4', 'CSRN3', 'CSRN5', 'CSRN6', 'CTCA3', 'DMMO3', 
                 'DTCY4', 'EEEL3', 'EEEL4', 'ELEK4', 'ELPL3', 'ENAT3', 'ENBR3', 'CATA3', 
                 'CATA4', 'CCXC3', 'FBMC4', 'FLEX3', 'FNCN3', 'FRTA3', 'FTRT3B', 'GETT11', 
                 'GETT3', 'GETT4', 'GNDI3', 'HBTS3', 'HBTS6', 'HGTX3', 'IDVL3', 'IDVL4', 
                 'IGBR3', 'IGTA3', 'INNT3', 'ITEC3', 'LAME3', 'LAME4', 'LCAM3', 'LHER3', 
                 'LHER4', 'LINX3', 'ENMA3B', 'MODL11', 'MODL3', 'MODL4', 'MOSI3', 'MSRO3', 
                 'MTIG4', 'NAFG3', 'NAFG4', 'NRTQ3', 'ODER3', 'OGXP3', 'OMGE3', 'PARD3', 
                 'PCAR4', 'PNVL4', 'POWE3', 'PTCA11', 'PTCA3', 'QUSW3', 'QVQP3B', 'RANI4', 
                 'LTEL3B', 'MMXM3', 'SEDU3', 'SMLS3', 'SOMA3', 'SPRT3B', 'SQIA3', 'STTR3', 
                 'SULA11', 'SULA3', 'SULA4', 'TCNO3', 'TCNO4', 'TESA3', 'TIET11', 'TIET3', 
                 'TIET4', 'TOYB3', 'TOYB4', 'VIVT4', 'RLOG3', 'STKF3', 'ADHM3', 'BRML3', 
                 'ELEK3', 'ENMA6B', 'FBMC3', 'GBIO33', 'GRAO3']
class Analysis:
    def __init__(self, ticker_list=None, days=30, min_volume=0):
        """
        Initialize Analysis class
        Args:
            ticker_list (list): Optional list of tickers to analyze. If None, uses all stocks.
            days (int): Number of days to analyze. Default is 30.
            min_volume (float): Minimum average volume to include stock. Default is 0 (no filter).
        """
        if ticker_list:
            self.list_all_ticker = ticker_list
        else:
            self.list_all_ticker = get_all_stocks()
        self.days = days
        self.min_volume = min_volume
        self.volume_data = []
        
    def process_volume_data(self):
        """Process volume data for all stocks"""
        
        for ticker in tqdm(self.list_all_ticker, desc="Processing volumes"):
            
            if ticker in list_delisted:
                continue
            
            historical_data = yf.Ticker(ticker+".SA").history(period=f"{self.days}d")
            if historical_data.empty:
                list_delisted.append(ticker)
                continue
            volume = Volume(ticker + ".SA", historical_data)
            prices = Prices(ticker + ".SA", historical_data)
            last_week = volume.last_week_volume
            last_week_prices = prices.last_week_prices
            
            if isinstance(last_week, str):
                if "delisted" in last_week.lower():
                    continue
            else:
                average = volume.get_average_last_week_volume()
                last_valid = volume.get_last_valid_volume()
                if(last_valid == "No valid non-zero volume found in the last week"):
                    continue
                if self.min_volume > 0 and average < self.min_volume:  # Skip low volume stocks only if min_volume is set
                    continue
                percentage = volume.get_last_valid_volume_percentage()
                
                # Get price variation
                price_percentage = prices.get_last_valid_price_percentage()
                if isinstance(price_percentage, str):
                    price_percentage = 0
                
                try:
                    if isinstance(last_valid, (int, float)):
                        numeric_volume = float(last_valid)
                    else:
                        numeric_volume = float(str(last_valid).replace(',', ''))
                    if numeric_volume > 0:
                        numeric_percentage = float(percentage)
                        numeric_average = float(average) if isinstance(average, (int, float)) else float(str(average).replace(',', ''))
                        
                        # Calculate percentage of time below averages
                        price_mean = historical_data['Close'].mean()
                        volume_mean = historical_data['Volume'].mean()
                        below_condition = (historical_data['Close'] < price_mean) & (historical_data['Volume'] < volume_mean)
                        condition_percentage = (below_condition.sum() / len(below_condition)) * 100
                        
                        self.volume_data.append([
                            ticker, 
                            numeric_volume, 
                            numeric_average, 
                            numeric_percentage, 
                            price_percentage,
                            condition_percentage
                        ])
                except:
                    continue
        
        # Sort by percentage of time below averages
        self.volume_data.sort(key=lambda x: x[5], reverse=True)
    
    def get_top_10_highest_volume(self):
        """Get top 10 highest volume variations"""
        return self.volume_data[:10]
    
    def get_top_10_lowest_volume(self):
        """Get top 10 lowest volume variations"""
        return self.volume_data[-10:]
    
    def create_volume_table_html(self, data, title):
        """Create HTML table for volume data"""
        html = f'<h2>{title}</h2>'
        html += '''
        <table class="volume-table">
            <tr>
                <th>Ticker</th>
                <th>Last Volume</th>
                <th>Average Volume</th>
                <th>Volume %</th>
                <th>Price %</th>
            </tr>
        '''
        
        for row in data:
            ticker_link = f'<a href="#chart_{row[0]}">{row[0]}</a>'
            html += f'''
            <tr>
                <td>{ticker_link}</td>
                <td>{format(row[1], '.0f')}</td>
                <td>{format(row[2], '.2f')}</td>
                <td>{format(row[3], '.2f')}%</td>
                <td>{format(row[4], '.2f')}%</td>
            </tr>
            '''
        
        html += '</table>'
        return html
    
    def create_specific_analysis(self, output_filename='specific_analysis.html'):
        """Create analysis for specific tickers"""
        self.process_volume_data()
        
        html_content = []
        html_content.append(f"""
        <html>
        <head>
            <title>Stock Analysis</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart-container {{ margin-bottom: 30px; }}
                h1, h2 {{ color: #333; }}
                .volume-table {{ border-collapse: collapse; margin: 20px 0; width: 100%; }}
                .volume-table th, .volume-table td {{ 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: right; 
                }}
                .volume-table th {{ 
                    background-color: #f5f5f5; 
                    position: sticky;
                    top: 0;
                }}
                .volume-table td:first-child {{ text-align: left; }}
                .volume-table a {{ color: #0066cc; text-decoration: none; }}
                .volume-table a:hover {{ text-decoration: underline; }}
                .table-container {{
                    margin-bottom: 30px;
                    max-height: 500px;
                    overflow-y: auto;
                }}
                .position-indicator {{
                    color: #ff0000;
                    font-weight: bold;
                    margin-left: 10px;
                }}
                .opportunity-row {{
                    background-color: black !important;
                    color: #32cd32 !important;
                    font-weight: bold;
                }}
                .opportunity-row a {{
                    color: #32cd32 !important;
                }}
            </style>
        </head>
        <body>
            <h1>Stock Analysis ({self.days} Days)</h1>
            <div class="table-container">
        """)
        
        # Add table with condition percentage column
        html_content.append('''
        <table class="volume-table">
            <tr>
                <th>Ticker</th>
                <th>Last Volume</th>
                <th>Average Volume</th>
                <th>Volume %</th>
                <th>Price %</th>
                <th>Below Avg %</th>
            </tr>
        ''')
        
        for row in self.volume_data:
            # Get current data to check conditions
            stock = yf.Ticker(row[0] + ".SA")
            hist = stock.history(period=f"{self.days}d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                current_volume = hist['Volume'].iloc[-1]
                price_mean = hist['Close'].mean()
                volume_mean = hist['Volume'].mean()
                
                # Get price target
                prices_instance = Prices(row[0] + ".SA", hist)
                ptarget = prices_instance.ptarget
                
                # Check if meets all conditions
                is_opportunity = (
                    current_volume < volume_mean and 
                    current_price < price_mean and 
                    ptarget is not None and 
                    ptarget > 0 and 
                    current_price < ptarget
                )
                
                row_class = 'opportunity-row' if is_opportunity else ''
                
                ticker_link = f'<a href="#chart_{row[0]}">{row[0]}</a>'
                html_content.append(f'''
                <tr class="{row_class}">
                    <td>{ticker_link}</td>
                    <td>{format(row[1], '.0f')}</td>
                    <td>{format(row[2], '.2f')}</td>
                    <td>{format(row[3], '.2f')}%</td>
                    <td>{format(row[4], '.2f')}%</td>
                    <td>{format(row[5], '.2f')}%</td>
                </tr>
                ''')
        
        html_content.append('</table></div>')
        
        # Create charts for all tickers
        for ticker_data in tqdm(self.volume_data, desc="Creating charts"):
            # Get historical data
            stock = yf.Ticker(ticker_data[0] + ".SA")
            hist = stock.history(period=f"{self.days}d")
            
            if not hist.empty:
                # Find the last valid volume date
                valid_volumes = hist[hist['Volume'] > 0]
                if not valid_volumes.empty:
                    last_valid_date = valid_volumes.index[-1]
                    # Filter data up to the last valid volume date
                    hist = hist[hist.index <= last_valid_date]
                
                # Create instances for analysis
                prices_instance = Prices(ticker_data[0] + ".SA", hist)
                volume_instance = Volume(ticker_data[0] + ".SA", hist)
                
                # Create figure with secondary y-axis
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Add price line
                fig.add_trace(
                    go.Scatter(x=hist.index, y=hist['Close'], name="Price", line=dict(color='#00ffff')),
                    secondary_y=False,
                )

                # Calculate and add price average line
                price_mean = hist['Close'].mean()
                fig.add_trace(
                    go.Scatter(
                        x=hist.index,
                        y=[price_mean] * len(hist.index),
                        name="Average Price",
                        line=dict(color='#ff69b4', dash='dash'),
                        opacity=0.7
                    ),
                    secondary_y=False,
                )

                # Add price target line if available
                ptarget = prices_instance.ptarget
                if ptarget is not None and ptarget > 0:
                    fig.add_trace(
                        go.Scatter(
                            x=hist.index,
                            y=[ptarget] * len(hist.index),
                            name="Price Target",
                            line=dict(color='#32cd32'),
                            opacity=0.9
                        ),
                        secondary_y=False,
                    )
                
                # Add volume line
                fig.add_trace(
                    go.Scatter(x=hist.index, y=hist['Volume'], name="Volume", line=dict(color='#ff4500')),
                    secondary_y=True,
                )
                
                # Calculate and add volume average line
                volume_mean = hist['Volume'].mean()
                fig.add_trace(
                    go.Scatter(
                        x=hist.index,
                        y=[volume_mean] * len(hist.index),
                        name="Average Volume",
                        line=dict(color='#ffd700', dash='dash'),
                        opacity=0.7
                    ),
                    secondary_y=True,
                )

                # Define condition where both price and volume are below average
                below_condition = (hist['Close'] < price_mean) & (hist['Volume'] < volume_mean)
                
                # Function to find interval boundaries
                def find_intervals(condition_series):
                    changes = condition_series.astype(int).diff()
                    starts = hist.index[changes == 1]
                    ends = hist.index[changes == -1]
                    
                    # Handle case where interval starts at beginning of data
                    if condition_series.iloc[0]:
                        starts = pd.Index([hist.index[0]]).append(starts)
                    
                    # Handle case where interval ends at end of data
                    if condition_series.iloc[-1]:
                        ends = ends.append(pd.Index([hist.index[-1]]))
                    
                    return list(zip(starts, ends))

                # Find intervals where condition is true
                intervals = find_intervals(below_condition)

                # Add vertical lines and shaded regions for the condition
                for start, end in intervals:
                    # Add vertical lines at start and end
                    fig.add_vline(x=start, line_width=2, line_dash="solid", 
                                line_color="#ff0000", opacity=0.2)
                    fig.add_vline(x=end, line_width=2, line_dash="solid", 
                                line_color="#ff0000", opacity=0.2)
                    
                    # Add shaded region between lines
                    fig.add_vrect(
                        x0=start, x1=end,
                        fillcolor="#ff0000", opacity=0.2,
                        layer="below", line_width=0,
                        name="Price & Volume Below Average"
                    )
                
                # Set titles and layout
                layout_dict = {
                    "title": f"{ticker_data[0]} - Price and Volume Analysis ({self.days} Days)",
                    "xaxis_title": "Date",
                    "yaxis_title": "Price (R$)",
                    "yaxis2_title": "Volume",
                    "height": 600,
                    "showlegend": True,
                    "legend": dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01,
                        font=dict(color='white')
                    ),
                    "margin": dict(l=50, r=50, t=50, b=50),
                    "paper_bgcolor": "black",
                    "plot_bgcolor": "black",
                    "font": dict(color="white"),
                    "xaxis": dict(
                        gridcolor='#333333',
                        zerolinecolor='#333333',
                    ),
                    "yaxis": dict(
                        gridcolor='#333333',
                        zerolinecolor='#333333',
                    ),
                    "yaxis2": dict(
                        gridcolor='#333333',
                        zerolinecolor='#333333',
                    )
                }
                
                fig.update_layout(**layout_dict)
                
                # Convert the plot to HTML
                chart_html = pio.to_html(fig, full_html=False)
                
                title_html = f'<h2>{ticker_data[0]} Analysis'
                if ticker_data[5] > 0:  # If there's any time below average
                    title_html += f' <span class="position-indicator">({ticker_data[5]:.1f}% Below Average)</span>'
                title_html += '</h2>'
                
                html_content.append(f'<div id="chart_{ticker_data[0]}" class="chart-container">')
                html_content.append(title_html)
                html_content.append(chart_html)
                html_content.append('</div>')
        
        html_content.append("""
        </body>
        </html>
        """)
        
        # Save the HTML file
        with open(output_filename, 'w') as f:
            f.write('\n'.join(html_content))
        
        print(f"Analysis complete! Open {output_filename} to view the analysis.")

def get_tickers_from_html(html_path='/var/www/html/index.html', limit=20):
    """
    Extract tickers from the HTML file
    Args:
        html_path (str): Path to the HTML file
        limit (int): Number of tickers to extract
    Returns:
        list: List of tickers
    """
    tickers = []
    try:
        print(f"Reading HTML file from: {html_path}")
        with open(html_path, 'r') as file:
            content = file.read()
            print(f"File size: {len(content)} bytes")
            
            # Find all ticker references in finance links
            matches = re.findall(r'finance/quote/([A-Z0-9]+):BVMF', content)
            print(f"Found {len(matches)} ticker matches in the HTML")
            
            # Take only the first 'limit' unique tickers
            tickers = list(dict.fromkeys(matches))[:limit]
            #add .SA to the tickers
            #tickers = [ticker + ".SA" for ticker in tickers]
            print(f"Extracted {len(tickers)} unique tickers: {tickers}")
            
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return []
    return tickers

if __name__ == "__main__":
    # Get tickers from HTML file
    specific_tickers = get_tickers_from_html()
    
    if not specific_tickers:
        print("No tickers found in HTML. Using default list.")
        specific_tickers = ["BMEB4"]
    
    print("Analyzing the following tickers:", specific_tickers)
    analysis = Analysis(specific_tickers, days=90, min_volume=0)  # No minimum volume filter
    analysis.create_specific_analysis('specific_analysis.html')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      