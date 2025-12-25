from dataclasses import dataclass
from typing import Optional, Tuple
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

@dataclass
class Stock:
    """
    A class representing a stock with its basic information and price data.
    This class provides methods to interact with the stock_indicators table in the database.
    """
    ticker: str
    company_name: str
    price: float
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    p_target: Optional[float] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_db(cls, ticker: str) -> Optional['Stock']:
        """
        Fetch stock data from the database for a given ticker.
        
        Args:
            ticker (str): The stock ticker symbol
            
        Returns:
            Optional[Stock]: A Stock instance if found, None otherwise
            
        Raises:
            Exception: If there's an error connecting to the database
        """
        db_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'yfinance',
            'user': 'postgres',
            'password': 'yfinance'
        }
        
        try:
            conn = psycopg2.connect(**db_config)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT ticker, company_name, price, price_min, price_max, 
                           p_target, updated_at
                    FROM stock_indicators
                    WHERE ticker = %s
                """, (ticker.upper(),))
                
                result = cur.fetchone()
                
                if result:
                    return cls(
                        ticker=result['ticker'],
                        company_name=result['company_name'],
                        price=float(result['price']),
                        price_min=float(result['price_min']) if result['price_min'] else None,
                        price_max=float(result['price_max']) if result['price_max'] else None,
                        p_target=float(result['p_target']) if result['p_target'] else None,
                        updated_at=result['updated_at']
                    )
                return None
                
        except Exception as e:
            raise Exception(f"Error fetching stock data: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def get_current_price(self) -> float:
        """
        Get the current price of the stock.
        
        Returns:
            float: The current price
        """
        return self.price

    def get_price_range(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the minimum and maximum price range of the stock.
        
        Returns:
            Tuple[Optional[float], Optional[float]]: A tuple containing (min_price, max_price)
        """
        return self.price_min, self.price_max

    def get_target_price(self) -> Optional[float]:
        """
        Get the target price of the stock.
        
        Returns:
            Optional[float]: The target price if available, None otherwise
        """
        return self.p_target

if __name__ == "__main__":
    stock = Stock.from_db("ITUB4")
    print(stock)