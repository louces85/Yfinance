import logging
from stock_indicators_repository import StockIndicatorsRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Database configuration
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'yfinance',
        'user': 'postgres',
        'password': 'yfinance'
    }

    # Path to your JSON file
    json_file_path = 'src_refator_version/indicators/all_stocks_and_indicators_2025.json'

    try:
        # Initialize repository
        repository = StockIndicatorsRepository(db_config)
        
        # Update stock indicators
        records_updated = repository.update_stock_indicators(json_file_path)
        
        logger.info(f"Successfully updated {records_updated} stock indicators")
        
    except Exception as e:
        logger.error(f"Error updating stock indicators: {str(e)}")
        raise

if __name__ == "__main__":
    main() 

