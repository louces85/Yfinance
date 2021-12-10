import psycopg2

class Connection_Factory:

    def __init__(self):
        self
    
    def connection(self):
        conn = psycopg2.connect(
        host='localhost',
        database='yfinance',
        user='postgres',
        password='yfinance')
        return conn