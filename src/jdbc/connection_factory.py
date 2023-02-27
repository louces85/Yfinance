import psycopg2

class Connection_Factory:

    def __init__(self):
        self
    
    def connection(self):
        conn = psycopg2.connect(
        host='172.18.0.2',
        database='yfinance',
        user='postgres',
        password='yfinance')
        return conn