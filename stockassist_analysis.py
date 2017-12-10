"""
stockassist_client library 

"""
import sys
import os
import pandas as pd
import numpy as mp
import datetime as dt
import matplotlib.pyplot as plt
import pickle
import monthdelta as md

from sklearn import datasets, linear_model
from operator import itemgetter
from heapq import nlargest

import stockassist_scrape as sa_scrape
import stockassist_core as sa_core

"""
"""

TICKER_FILE = '{}/{}_TOP_{}.pickle'.format(sa_core.ROOT, sa_core.MARKET, sa_core.MONTHS)

def get_top_coefficients(tickers,top, start_time, end_time, loadfromfile =False):
    sa_core.Print('get_top_coefficients')   
    ranking = {}
    if loadfromfile:
        with open(TICKER_FILE,'rb') as f:
            ranking = pickle.load(f)
        return ranking

    market_data = sa_scrape.load_market_data(start_time, end_time)
    for ticker in tickers:
        sa_core.Print('calculating coefficient:{}'.format(ticker))
        stock_data = sa_scrape.get_ticker_historical_data(ticker, start_time, end_time)
        if stock_data.empty or len(stock_data) < 2:
            continue
        model_data = pd.merge(market_data, stock_data, how='inner', on=['Date'])
        model_data['Date'] = pd.to_datetime(model_data['Date'], format='%Y-%m-%d')
        model_data.set_index('Date', inplace=True)       
        model_data = model_data.ix[pd.to_datetime('{:%Y-%m-%d}'.format(start_time)):pd.to_datetime('{:%Y-%m-%d}'.format(end_time))]
        # model_data = model_data[model_data['Returns_x'] > 0]
        model_data.dropna(how='any',inplace=True)
        sa_core.Print(model_data.head())
        if model_data.empty or len(model_data) < 10:
            continue       
        model_xData = model_data['Returns_x'][:-1].values.reshape(-1,1)
        model_yData = model_data['Returns_y'][:-1]
        model = linear_model.LinearRegression()
        model.fit(model_xData, model_yData)
        sa_core.Print('coefficient for {} is {}'.format(ticker, model.coef_))
        score = model.score(model_xData, model_yData)
        if score < sa_core.THRESHOLD_SCORE:
            continue
        ranking[ticker] = model.coef_
    sorted_dict = sorted(ranking.items(), key=itemgetter(1),reverse=True)[:top] 
    with open(TICKER_FILE, 'wb') as f:
        pickle.dump(sorted_dict,f)
    return sorted_dict

def plot_figure(ticker, start_time, end_time):
    sa_core.Print('plot_figure')
    market_data = sa_scrape.load_market_data(start_time, end_time)
    stock_data = sa_scrape.get_ticker_historical_data(ticker, start_time, end_time)
    sa_core.Print('stock data found:{}'.format(len(stock_data)))
    if not (stock_data.empty or len(stock_data) < 2):
        model_data = pd.merge(market_data, stock_data, how='inner', on=['Date'])
        model_data['Date'] = pd.to_datetime(model_data['Date'], format='%Y-%m-%d')
        model_data.set_index('Date', inplace=True)
        model_data = model_data.ix[pd.to_datetime('{:%Y-%m-%d}'.format(start_time)):pd.to_datetime('{:%Y-%m-%d}'.format(end_time))]
        model_data.dropna(how='any',inplace=True)
        sa_core.Print('model data found:{}'.format(len(model_data)))
        if not (model_data.empty or len(model_data) < 20):
            model_xData = model_data['Returns_x'][:-1].values.reshape(-1,1)
            model_yData = model_data['Returns_y'][:-1]
            model = linear_model.LinearRegression()
            model.fit(model_xData, model_yData)
            score = model.score(model_xData, model_yData)
            sa_core.Print(ticker + ' ' + str(model.coef_) + ' ' + '{:0.2f}'.format(score))   
            plt.scatter(model_xData,model_yData, color='blue')
            plt.plot(model_xData, model.predict(model_xData), color='green', linewidth=1)
    plt.xticks([])
    plt.yticks([])
    plt.show()


def plot_figures(tickers, start_time, end_time):
    sa_core.Print('plot_figures')
    market_data = sa_scrape.load_market_data(start_time, end_time)
    fig, ax = plt.subplots(nrows=5,ncols=5)
    fig.tight_layout
    ctr = 1
    for ticker in tickers:
        sa_core.Print('plot figures:{}'.format(ticker))
        stock_data = sa_scrape.get_ticker_historical_data(ticker, start_time, end_time)
        if stock_data.empty or len(stock_data) < 2:
            continue
        model_data = pd.merge(market_data, stock_data, how='inner', on=['Date'])
        model_data['Date'] = pd.to_datetime(model_data['Date'], format='%Y-%m-%d')
        model_data.set_index('Date', inplace=True)
        model_data = model_data.ix[pd.to_datetime('{:%Y-%m-%d}'.format(start_time)):pd.to_datetime('{:%Y-%m-%d}'.format(end_time))]
        model_data.dropna(how='any',inplace=True)
        if model_data.empty or len(model_data) < 20:
            continue       
        model_xData = model_data['Returns_x'][:-1].values.reshape(-1,1)
        model_yData = model_data['Returns_y'][:-1]
        model = linear_model.LinearRegression()
        model.fit(model_xData, model_yData)
        score = model.score(model_xData, model_yData)
        ax = plt.subplot(5,5,ctr)
        ax.set_title(ticker + ' ' + str(model.coef_) + ' ' + '{:0.2f}'.format(score))   
        plt.scatter(model_xData,model_yData, color='blue')
        plt.plot(model_xData, model.predict(model_xData), color='green', linewidth=1)
        plt.xticks([])
        plt.yticks([])
        #plt.axis([min(model_data['Returns_x']),max(model_data['Returns_x']),min(model_data['Returns_y']),max(model_data['Returns_y'])])
        ctr = ctr+1
    plt.show()


#start_time = dt.datetime(2016,12,1)
#end_time = dt.datetime(2017,12,1)
start_time = dt.datetime.today() - md.monthdelta(sa_core.MONTHS)
end_time = dt.datetime.today()
print("MARKET: {} Start Date: {:%Y-%m-%d} End Date: {:%Y-%m-%d}".format(sa_core.MARKET, start_time, end_time))


#tickers = sa_scrape.get_all_ticker_symbols_from_file()
#top_tickers = get_top_coefficients(tickers[:],25, start_time, end_time,False)
plot_figure('WSC',start_time, end_time)
#plot_figures(dict(top_tickers).keys(), start_time, end_time)