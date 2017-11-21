"""
stockassist_scrape library 
"""
import sys
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import bs4 as bs
import pickle

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'}
MARKET = 'nasdaq'
ROOT = 'c:/dawa/stockassist'
TICKER_FILE = '{}/{}.pickle'.format(ROOT, MARKET) 

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
#ticker_symbols = get_all_ticker_symbols()

ticker_symbols = get_all_ticker_symbols_from_file()



# for ticker_symbol in ticker_symbols:
#     print(ticker_symbol)