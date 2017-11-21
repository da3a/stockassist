"""
stockassist_scrape library 
"""
import sys
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'}
MARKEY = 'nasdaq'

url = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&pagesize=200&page={}'

def scrape_nasdaq_ticker_symbols(pageNo):
    print('scrape_ticker_symbols pageNo:{}'.format(pageNo))
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(url.format(pageNo), headers = HEADERS, verify=False)
    soup = bs.BeautifulSoup(response.text,'lxml')
    table = soup.find('table',id='Companylistresults')
    ticker_symbols = []
    for row in table.findAll('tr')[1:]:
        if len(row.findAll('td')) > 1:
            ticker_symbol = row.findAll('td')[1].text.rstrip().lstrip()
            ticker_symbols.append(ticker_symbol)
    return ticker_symbols



if __main__ == '__main__':
    print('running library')
