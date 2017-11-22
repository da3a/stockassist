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

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'}
MARKET = 'nasdaq'
ROOT = 'c:/dawa/stockassist'
TICKER_FILE = '{}/{}.pickle'.format(ROOT, MARKET)
MARKETDATA = '^NDX.csv'

url = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&pagesize=200&page={}'

def scrape_nasdaq_ticker_symbols(pageNo):
    print('scrape_ticker_symbols pageNo:{}'.format(pageNo))
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(url.format(pageNo), headers = HEADERS, verify=False)
    soup = bs.BeautifulSoup(response.text,'lxml')
    table = soup.find('table',id='CompanylistResults')
    ticker_symbols = []
    for row in table.findAll('tr')[1:]:
        if len(row.findAll('td')) > 1:
            ticker_symbol = row.findAll('td')[1].text.rstrip().lstrip()
            ticker_symbols.append(ticker_symbol)
    return ticker_symbols


def get_all_ticker_symbols_from_web():
    print('get_all_ticker_symbols')
    pageCnt = 0
    pageTotal = 16
    ticker_symbols = []
    while pageCnt < pageTotal:
        pageCnt = pageCnt + 1
        paged_ticker_symbols = scrape_nasdaq_ticker_symbols(pageCnt)
        ticker_symbols.extend(paged_ticker_symbols)
    return ticker_symbols

# if __main__ == '__main__':
#     print('running library')

def save_all_ticker_symbols():
    ticker_symbols = get_all_ticker_symbols_from_web()

    with open(TICKER_FILE, 'wb') as f:
        pickle.dump(ticker_symbols,f)

def get_all_ticker_symbols_from_file():
    with open(TICKER_FILE,'rb') as f:
        ticker_symbols = pickle.load(f)
    return ticker_symbols

def get_ticker_historical_data_from_web(ticker_symbol, start_time, end_time):
    print('get_ticker_historical_data_from_web {} {} {}'.format(ticker_symbol, start_time, end_time))
    try:
        df = web.DataReader(ticker_symbol,'google',start_time, end_time)
        df.to_csv('{}/{}/{}.csv'.format(ROOT, MARKET,ticker_symbol))
        return df
    except:
        return pd.DataFrame({'empty':[]})

def read_ticker_historical_file(file_name):
    print('read_ticker_historical_file {}'.format(file_name))
    data = pd.read_csv(file_name, sep=',',usecols=[0,4],names=['Date','Price'],header=1)
    returns = np.array(data['Price'][1:],np.float)/np.array(data['Price'][:-1],np.float)-1
    data['Returns'] = np.append(returns,np.nan)      
    data.index = data['Date']
    return data

def get_ticker_historical_data(ticker_symbol, start_time, end_time):
    file_name = '{}/{}/{}.csv'.format(ROOT, MARKET,ticker_symbol)
    if not os.path.isfile(file_name):
        get_ticker_historical_data_from_web(ticker_symbol, start_time, end_time)
    try:
        return read_ticker_historical_file(file_name)
    except:
        return pd.DataFrame({'empty':[]})


def load_market_data():
    file_name = '{}/{}'.format(ROOT, MARKETDATA)
    market_data = pd.read_csv(file_name,sep=',',usecols=[0,5],names=['Date','Price'],header=1)
    market_returns = np.array(market_data['Price'][1:],np.float)/np.array(market_data['Price'][:-1],np.float)-1
    market_data['Returns'] =np.append(market_returns, np.nan)
    market_data.index = market_data['Date']
    return market_data

#ticker_symbols = get_all_ticker_symbols()

if __name__ == "__main__":
    start_time = dt.datetime(2017,1,1)
    end_time = dt.datetime(2017,11,1)
    ticker_symbols = get_all_ticker_symbols_from_file()
    for ticker_symbol in ticker_symbols[:]:
        file_name = '{}/{}/{}.csv'.format(ROOT, MARKET,ticker_symbol)
        #get_ticker_historical_data_from_web(ticker_symbol, start_time, end_time)
        data = get_ticker_historical_data(ticker_symbol, start_time, end_time)
        print(data.head()) 