# YFinance
[![NPM](https://img.shields.io/npm/l/react)](https://github.com/louces85/Yfinance/blob/master/LICENSE) 

# About the project

YFinance is an application that helps you analyze stocks registered on B3 (BM & FBOVESPA). What motivated the development of this application was to look for good stocks that are in a downtrend in the last 6 months.

The application consists of a search of a previous list of goods registered in configuration files, comparing their current price with the maximum and minimum prices of the last 6 months. The stocks are ordered in relation to the R$ ratio (current price/minimum price) <= 1.1 , therefore, we get a list of stocks that are close to 10% of hitting the last 6 months' low price.

PS: It is important to emphasize that the application will only provide the analysis of stocks that have a positive balance in the last 4 years.

## Layout Web
![Web 1](https://github.com/louces85/Yfinance/blob/master/assets/main.png)

# Technologies used
## Backend
- Python
- Java
- Shell Script

## Frontend
- HTML/CSS

## Prerequisites:
  - Ubuntu 20.04 or similar distribution
 - Python 3
 - Pip3
 - Java 8

# How to run the project

```bash

# create project folder
mkdir ~/Documents/YFinance

# enter the project folder
cd ~/Documents/YFinance/

# clone repository
https://github.com/louces85/Yfinance.git

# install the dependencies
pip3 install config/requirements -U

# run the project
./run.sh

# open application in browser
google-chrome index.html
```
# How to update stocks price history
It is recommended to update the price history every 7 days. This procedure may take a few minutes, so it is recommended that it be performed after the trading session.
PS: In the first execution this file is absent, being necessary to run the script below for its creation.

```bash

~/Documents/Yfinance/history_6mo.py

```
# Changing the stocks that will be analyzed
stocks can be changed in the following configuration file:

```bash

vim ~/Documents/Yfinance/files/stocks_file

```

# Author

Fabiano Louzada Cesario

https://www.linkedin.com/in/fabiano-louzada-cesario/

