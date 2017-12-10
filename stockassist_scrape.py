"""
stockassist_scrape library 
"""
import sys
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import bs4 as bs
import pickle
import datetime as dt
import pandas_datareader.data as web
import pandas as pd
import numpy as np
import monthdelta as md

import stockassist_core as sa_core

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'}
TICKER_FILE = '{}/{}_symbols.pickle'.format(sa_core.ROOT, sa_core.MARKET)
SOURCE = 'yahoo' # or google - now not working when last tried ?

url_nasdaq= 'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&pagesize=200&page={}'
url_ftse = 'http://www.londonstockexchange.com/exchange/prices-and-markets/stocks/indices/summary/summary-indices-constituents.html?index=ASX&page={}'

def scrape_url(url):
    sa_core.Print('scrape_url url:{}'.format(url))
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(url, headers = HEADERS, verify=False)
    soup = bs.BeautifulSoup(response.text,'lxml')
    return soup

def scrape_nasdaq_ticker_symbols(pageNo):
    sa_core.Print('scrape_ticker_symbols pageNo:{}'.format(pageNo))
    soup = scrape_url(url_nasdaq.format(pageNo))
    table = soup.find('table',id='CompanylistResults')
    ticker_symbols = []
    for row in table.findAll('tr')[1:]:
        if len(row.findAll('td')) > 1:
            ticker_symbol = row.findAll('td')[1].text.rstrip().lstrip()
            ticker_symbols.append(ticker_symbol)
    return ticker_symbols

def scrape_ftse_ticker_symbols(pageNo):
    sa_core.Print("scrape_ftse_tickers pageNo:".format(pageNo))
    soup = scrape_url(url_ftse.format(pageNo))
    table = soup.find('table',{'class','table_dati'})
    ticker_symbols = []
    for row in table.findAll('tr')[1:]:
        ticker_symbol = row.findAll('td')[0].text
        ticker_symbols.append(ticker_symbol)
    return ticker_symbols

def get_all_ticker_symbols_from_web():
    sa_core.Print('get_all_ticker_symbols')
    pageCnt = 0
    pageTotal = sa_core.MARKET_PAGE_TOTAL
    ticker_symbols = []
    while pageCnt < pageTotal:
        pageCnt = pageCnt + 1
        if sa_core.MARKET == 'nasdaq':
            paged_ticker_symbols = scrape_nasdaq_ticker_symbols(pageCnt)
        elif sa_core.MARKET =='ftse':
            paged_ticker_symbols = scrape_ftse_ticker_symbols(pageCnt)
        ticker_symbols.extend(paged_ticker_symbols)
    return ticker_symbols

def save_all_ticker_symbols():
    sa_core.Print('save_all_ticker_symbols')
    ticker_symbols = get_all_ticker_symbols_from_web()
    with open(TICKER_FILE, 'wb') as f:
        pickle.dump(ticker_symbols,f)

def get_all_ticker_symbols_from_file():   
    sa_core.Print('get_all_ticker_symbols_from_file')
    try:
        with open(TICKER_FILE,'rb') as f:
            ticker_symbols = pickle.load(f)
        return ticker_symbols
    except:
        sa_core.Print('Reloading Ticker Symbols:{0}'.format(sys.exc_info()))
        save_all_ticker_symbols()
        with open(TICKER_FILE,'rb') as f:
            ticker_symbols = pickle.load(f)
        return ticker_symbols

def get_ticker_historical_data_from_web(ticker_symbol, start_time, end_time):
    sa_core.Print('get_ticker_historical_data_from_web ticker_Symbol:{} start_time:{} end_time:{}'.format(ticker_symbol, start_time, end_time))
    try:
        df = web.DataReader(ticker_symbol,SOURCE,start_time, end_time)
        file_name = '{}/{}/{}.csv'.format(sa_core.ROOT, sa_core.MARKET,ticker_symbol)
        sa_core.Print('writing to file:'.format(file_name))
        df.to_csv(file_name)
        return df
    except:
        sa_core.Print('exception writing file:{0}'.format(sys.exc_info()))
        return pd.DataFrame({'empty':[]})

def read_ticker_historical_file(file_name):
    sa_core.Print('read_ticker_historical_file {}'.format(file_name))
    data = pd.read_csv(file_name, sep=',',usecols=[0,4],names=['Date','Price'],header=1)
    returns = np.array(data['Price'][1:],np.float)/np.array(data['Price'][:-1],np.float)-1
    data['Returns'] = np.append(returns,np.nan)      
    data.index = data['Date']
    return data

def get_ticker_historical_data(ticker_symbol, start_time, end_time):
    file_name = '{}/{}/{}.csv'.format(sa_core.ROOT, sa_core.MARKET,ticker_symbol)
    sa_core.Print('reading file:{}'.format(file_name))
    if not os.path.isfile(file_name) and sa_core.RELOAD_MISSING_DATA:
        sa_core.Print('file not found'.format(file_name))
        get_ticker_historical_data_from_web(ticker_symbol, start_time, end_time)
    try:
        return read_ticker_historical_file(file_name)
    except:
        print('exception writing file:{0}'.format(sys.exc_info()))      
        return pd.DataFrame({'empty':[]})

#manually download this from here:
#https://uk.finance.yahoo.com/quote/%5ENDX/history?period1=1354924800&period2=1512691200&interval=1d&filter=history&frequency=1d
def load_market_data(start_time, end_time):
    sa_core.Print('load_market_data start_time:{:%Y-%m-%d} end_time:{:%Y-%m-%d}'.format(start_time, end_time))
    file_name = '{}/{}/{}.csv'.format(sa_core.ROOT, sa_core.MARKET, sa_core.MARKETDATA_SYMBOL)
    if not os.path.isfile(file_name):
        get_ticker_historical_data_from_web(sa_core.MARKETDATA_SYMBOL, start_time, end_time)

    market_data = pd.read_csv(file_name,sep=',',usecols=[0,5],names=['Date','Price'],header=1)
    market_returns = np.array(market_data['Price'][1:],np.float)/np.array(market_data['Price'][:-1],np.float)-1
    market_data['Returns'] =np.append(market_returns, np.nan)
    market_data.index = market_data['Date']
    return market_data

if __name__ == "__main__":
    print('StockAssist Scraper Module')
    #step 1 get some tickers
    get_all_ticker_symbols_from_file()
    #step 2 download the load the market data
    start_time = dt.datetime.today() - md.monthdelta(sa_core.MONTHS)
    end_time = dt.datetime.today()
    load_market_data(start_time, end_time)
    ticker_symbols = get_all_ticker_symbols_from_file()
    if sa_core.confirm_choice() == 'c':
        for ticker_symbol in ticker_symbols[:]:
            sa_core.Print('ticker:{}'.format(ticker_symbol))
            get_ticker_historical_data_from_web(ticker_symbol, start_time, end_time)
    #       

        # file_name = '{}/{}/{}.csv'.format(ROOT, MARKET,ticker_symbol)
        # get_ticker_historical_data(ticker_symbol, start_time, end_time)
#         ##data = get_ticker_historical_data(ticker_symbol, start_time, end_time)
#         #print(data.head()) 