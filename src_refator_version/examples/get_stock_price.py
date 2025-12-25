# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src_refator_version ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.stock import Stock

def main():
    # Exemplo com ITUB4
    ticker = "ITUB4"
    
    stock = Stock.from_db(ticker)
    preco_atual = stock.get_current_price()
    print(f"Preço atual: R$ {preco_atual:.2f}")
        

if __name__ == "__main__":
    main() 