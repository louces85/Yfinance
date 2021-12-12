#!/bin/bash

function create_data_base(){
    docker exec -it yfinance-postgres psql -U postgres yfinance -c "CREATE TABLE if not exists history ( id SERIAL PRIMARY KEY, ticker VARCHAR(7) NOT null UNIQUE, price_min float8 null, price_max float8 null, net_income boolean null, date_update date null );"
    docker exec -it yfinance-postgres psql -U postgres yfinance -c "CREATE TABLE if not exists stock ( id SERIAL PRIMARY KEY, ticker VARCHAR(7) NOT null UNIQUE );"
    docker exec -it yfinance-postgres psql -U postgres yfinance -c "CREATE TABLE if not exists valuation ( id SERIAL PRIMARY KEY, ticker VARCHAR(7) NOT null UNIQUE, price_target float8 null, payout float8 null );"
    docker exec -it yfinance-postgres psql -U postgres yfinance -c "CREATE TABLE if not exists price ( id SERIAL PRIMARY KEY, ticker VARCHAR(7) NOT null UNIQUE, price_now float8 null );"
}
create_data_base()