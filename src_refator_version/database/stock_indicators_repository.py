import json
import logging
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

class StockIndicatorsRepository:
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize the repository with database configuration.
        
        Args:
            db_config (Dict[str, str]): Database configuration parameters
                Required keys: host, port, database, user, password
        """
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    def _get_connection(self):
        """Create and return a database connection."""
        try:
            return psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            raise

    def update_stock_indicators(self, json_file_path: str) -> int:
        """
        Update stock indicators from a JSON file, processing one record at a time.
        Only processes predefined fields to ensure consistency.
        
        Args:
            json_file_path (str): Path to the JSON file containing stock indicators
            
        Returns:
            int: Number of records updated
        """
        try:
            # Read JSON file
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, dict) or 'list' not in data:
                raise ValueError("JSON file must contain a 'list' key with stock indicators")

            stock_list = data['list']
            if not isinstance(stock_list, list):
                raise ValueError("The 'list' key must contain an array of stock indicators")

            # Define the expected fields and their JSON mappings
            field_mappings = {
                'company_id': 'companyid',
                'company_name': 'companyname',
                'ticker': 'ticker',
                'price': 'price',
                'p_l': 'p_l',
                'dy': 'dy',
                'p_vp': 'p_vp',
                'p_ebit': 'p_ebit',
                'p_ativo': 'p_ativo',
                'ev_ebit': 'ev_ebit',
                'margem_bruta': 'margembruta',
                'margem_ebit': 'margemebit',
                'margem_liquida': 'margemliquida',
                'p_sr': 'p_sr',
                'p_ativo_circulante': 'p_ativocirculante',
                'giro_ativos': 'giroativos',
                'roe': 'roe',
                'roa': 'roa',
                'pl_ativo': 'pl_ativo',
                'passivo_ativo': 'passivo_ativo',
                'peg_ratio': 'peg_ratio',
                'receitas_cagr5': 'receitas_cagr5',
                'lucros_cagr5': 'lucros_cagr5',
                'liquidez_media_diaria': 'liquidezmediadiaria',
                'vpa': 'vpa',
                'lpa': 'lpa',
                'valor_mercado': 'valormercado',
                'segment_id': 'segmentid',
                'sector_id': 'sectorid',
                'subsector_id': 'subsectorid',
                'subsector_name': 'subsectorname',
                'segment_name': 'segmentname',
                'sector_name': 'sectorname'
            }

            # Define numeric fields that should be positive
            positive_numeric_fields = {
                'price': 'Preço',
                'valor_mercado': 'Valor de Mercado',
                'liquidez_media_diaria': 'Liquidez Média Diária'
            }

            records_processed = 0
            conn = self._get_connection()
            
            try:
                for item in stock_list:
                    if item.get('price') is None or item.get('price') <= 0:
                        continue
                    if item.get('valormercado') is None or item.get('valormercado') <= 0:
                        continue
                    if item.get('liquidezmediadiaria') is None or item.get('liquidezmediadiaria') <= 0:
                        continue
                    try:
                        # Create record with only the predefined fields
                        record = {}
                        for db_field, json_field in field_mappings.items():
                            value = item.get(json_field)
                            
                            # Convert numeric fields
                            if db_field in positive_numeric_fields:
                                try:
                                    if value is not None:
                                        value = float(value)
                                        if value <= 0:
                                            self.logger.warning(
                                                f"Skipping record for {item.get('ticker', 'unknown')}: "
                                                f"{positive_numeric_fields[db_field]} must be positive, got {value}"
                                            )
                                            continue
                                except (ValueError, TypeError):
                                    self.logger.warning(
                                        f"Skipping record for {item.get('ticker', 'unknown')}: "
                                        f"Invalid {positive_numeric_fields[db_field]} value: {value}"
                                    )
                                    continue
                            
                            record[db_field] = value

                        # Skip if no company_id (required field)
                        if not record['company_id']:
                            self.logger.warning(f"Skipping record with no company_id: {item.get('ticker', 'unknown')}")
                            continue

                        with conn.cursor() as cur:
                            # Check if record exists
                            cur.execute(
                                "SELECT company_id FROM stock_indicators WHERE company_id = %s",
                                (record['company_id'],)
                            )
                            exists = cur.fetchone() is not None

                            if exists:
                                # Update existing record
                                update_fields = []
                                update_values = []
                                
                                # Build dynamic update query based on available fields
                                for field in field_mappings.keys():
                                    if field != 'company_id':  # Skip company_id in SET clause
                                        update_fields.append(f"{field} = COALESCE(%s, {field})")
                                        update_values.append(record[field])
                                
                                update_query = f"""
                                    UPDATE stock_indicators
                                    SET {', '.join(update_fields)},
                                        updated_at = CURRENT_TIMESTAMP
                                    WHERE company_id = %s
                                """
                                update_values.append(record['company_id'])
                                
                                cur.execute(update_query, tuple(update_values))
                            else:
                                # Insert new record
                                fields = list(field_mappings.keys())
                                placeholders = ['%s'] * len(fields)
                                
                                insert_query = f"""
                                    INSERT INTO stock_indicators (
                                        {', '.join(fields)}
                                    ) VALUES (
                                        {', '.join(placeholders)}
                                    )
                                """
                                
                                insert_values = [record[field] for field in fields]
                                cur.execute(insert_query, tuple(insert_values))

                            # Commit after each successful record
                            conn.commit()
                            records_processed += 1
                            self.logger.info(f"Processed record {records_processed}: {record.get('ticker', 'unknown')}")

                    except Exception as e:
                        # Rollback on error and log it
                        conn.rollback()
                        self.logger.error(f"Error processing record for ticker {item.get('ticker', 'unknown')}: {str(e)}")
                        continue

            finally:
                # Ensure connection is closed
                conn.close()

            return records_processed

        except Exception as e:
            self.logger.error(f"Error updating stock indicators: {str(e)}")
            raise 