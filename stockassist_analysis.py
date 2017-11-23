"""
stockassist_client library 

"""
import sys
import os
import stockassist_scrape as sa_scrape
import pandas as pd
import numpy as mp
import datetime as dt
import matplotlib.pyplot as plt

from sklearn import datasets, linear_model
from operator import itemgetter
from heapq import nlargest
"""
"""


def get_top_coefficients(tickers,top, start_time, end_time):
    ranking = {}
    market_data = sa_scrape.load_market_data()
    for ticker in tickers:
        df = sa_scrape.get_ticker_historical_data(ticker, start_time, end_time)
        if df.empty or len(df) < 2:
            continue
        model_data = pd.merge(market_data, df, how='inner', on=['Date'])
        model_xData = model_data['Returns_x'][:-1].values.reshape(-1,1)
        model_yData = model_data['Returns_y'][:-1]
        model = linear_model.LinearRegression()
        model.fit(model_xData, model_yData)
        print('coefficient for {} is {}'.format(ticker, model.coef_))
        ranking[ticker] = model.coef_   
    return sorted(ranking.items(), key=itemgetter(1),reverse=True)[:top]

def plot_figures(tickers):
    market_data = sa_scrape.load_market_data()
    fig, ax = plt.subplots(nrows=5,ncols=5)
    fig.tight_layout
    ctr = 1
    for ticker in tickers:
        print('plot figures:{}'.format(ticker))
        df = sa_scrape.get_ticker_historical_data(ticker, start_time, end_time)
        if df.empty or len(df) < 2:
            continue
        model_data = pd.merge(market_data, df, how='inner', on=['Date'])
        model_xData = model_data['Returns_x'][:-1].values.reshape(-1,1)
        model_yData = model_data['Returns_y'][:-1]
        model = linear_model.LinearRegression()
        model.fit(model_xData, model_yData)
        ax = plt.subplot(5,5,ctr)
        ax.set_title(ticker + ' ' + str(model.coef_))   
        plt.scatter(model_xData,model_yData, color='blue')
        plt.plot(model_xData, model.predict(model_xData), color='green', linewidth=1)
        plt.axis([min(model_data['Returns_x']),max(model_data['Returns_x']),min(model_data['Returns_y']),max(model_data['Returns_y'])])
        ctr = ctr+1
    plt.show()

start_time = dt.datetime(2017,1,1)
end_time = dt.datetime(2017,11,1)
tickers = sa_scrape.get_all_ticker_symbols_from_file()
top_tickers = get_top_coefficients(tickers[:500],25, start_time, end_time)
plot_figures(dict(top_tickers).keys())