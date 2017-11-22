"""
stockassist_client library 

"""
import sys
import os
import stockassist_scrape as sa_scrape
import pandas as pd
import numpy as mp
import datetime as dt


from sklearn import datasets, linear_model
from operator import itemgetter
from heapq import nlargest
"""
"""
def get_coefficients(tickers,top, start_time, end_time):
    ranking = {}
    market_data = sa_scrape.load_market_data()
    for ticker_symbol in tickers:
        df = sa_scrape.get_ticker_historical_data(ticker_symbol, start_time, end_time)
        if df.empty or len(df) < 2:
            continue
        model_data = pd.merge(market_data, df, how='inner', on=['Date'])
        year_xData = model_data['Returns_x'][:-1].values.reshape(-1,1)
        year_yData = model_data['Returns_y'][:-1]
        year_model = linear_model.LinearRegression()
        year_model.fit(year_xData, year_yData)
        #print('coefficient for {} is {}'.format(ticker_symbol,year_model.coef_))
        ranking[ticker_symbol] = year_model.coef_   
    return sorted(ranking.items(), key=itemgetter(1),reverse=True)[:top]


start_time = dt.datetime(2017,1,1)
end_time = dt.datetime(2017,11,1)

ticker_symbols = sa_scrape.get_all_ticker_symbols_from_file()
get_coefficients(ticker_symbols[:100],5, start_time, end_time)