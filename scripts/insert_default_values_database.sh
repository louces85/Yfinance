#!/bin/bash

stocks=`cat ../files/stocks_file`

function insert_values_stock(){
    for k in $stocks
    do
        docker exec -it yfinance-postgres psql -U postgres yfinance -c "insert into stock (ticker) values ('$k');"
    done
}

function insert_values_price(){
    for k in $stocks
    do
        docker exec -it yfinance-postgres psql -U postgres yfinance -c "insert into price (ticker, price_now) values ('$k', 0);"
    done
}

function insert_values_history(){
    for k in $stocks
    do
        docker exec -it yfinance-postgres psql -U postgres yfinance -c "insert into history (ticker, price_min, price_max, net_income, date_update) values ('$k', 0, 0, false, '1969-12-31');"
    done
}

function insert_values_valuation(){
    for k in $stocks
    do
        docker exec -it yfinance-postgres psql -U postgres yfinance -c "insert into valuation (ticker, price_target, payout) values ('$k', 0, 0);"
    done
}

insert_values_stock()
insert_values_price()
insert_values_history()
insert_values_valuation()