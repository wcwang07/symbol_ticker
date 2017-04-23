""" This module defines functions for searching for information
about countries listed in the CIA World Factbook. """
from __future__ import print_function
import requests
import re
import sys
import quandl
import json

import urllib
import datetime
import StringIO

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from collections import OrderedDict

keywords = {"Area": "Area", "Population": "Population", "Capital": "Capital", "Languages": "Languages", "Currency": "Exchange rates"}
url = "https://www.cia.gov/library/publications/the-world-factbook/"

def get_info(search_term):
    """ The initial function called to start a searching process. Takes a 
    search term as an argument and checks to see whether the term is an
    attribute (e.g. Population) or a country. If it is an attribute,
    a dictionary mapping every country to its data for that attribute is 
    returned. If the search term is a country, a dictionary mapping
    a pre-selected set of attributes to the data for that country is 
    returned. 
    :param search_term: country or keyword request.  
    :type search_term: str.
    :returns: Dict. or None.
    :raises: None.

    """
    
    print ("Enter get_info with entry = ")
    tickers=search_term.split(" ")

    for word in tickers:
        print (word)

	
    print (search_term)
    #sdate = raw_input("Start date: ")
    quandl.ApiConfig.api_key = 'Y9_e8-y8SD1kMQSYSCW9' 
    data = quandl.get_table('WIKI/PRICES', paginate=True, qopts = { 'columns': ['ticker','date', 'close'] }, ticker = tickers, date = { 'gte': '2016-10-01', 'lte': '2016-12-31' })

    return data

def graph(data):
    print("enter graph")
    fig=Figure()

    ax=fig.add_subplot(111)
    ax.xaxis_date()

    #text = request.form['search']
    #return a list
    tickerlist=[]
    print("size of data"+str(len(data)))

    #filter out uniques ticker
    for elt in range(len(data)):
        tickerlist.append(data.iloc[elt,0])

    uniques = set(tickerlist)
    
    luniques=list(uniques)
    #add to each ticker x values and y values
    x=[]
    y=[]
    for elt in uniques:
        grouped=data[data['ticker']==elt]
        dlist=[]
        plist=[]
        for row in range(len(grouped)):
            dlist.append(str(grouped.iloc[row,1].date()))
            plist.append(grouped.iloc[row,2])
        x.append(dlist)
        y.append(plist)

    #print("value of first ticker x="+str(len(x[0])))
    # print("value of first ticker y="+str(y[0]))


    delta=datetime.timedelta(days=1)
    for row in range(len(x)):
        ax.plot_date(x[row], y[row], '-', label= luniques[row])
    #legend takes as argument a list of axis handles and labels, defaulting to get_legend_handles_labels()
    handles, labels = ax.get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())

    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    fig.autofmt_xdate()

    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    png_output = png_output.getvalue().encode("base64")

    return png_output

	
def get_info_table(search_term):
    print("enter get_info_table");
    data=get_info(search_term)
    b={}
    
    tickerlist=[]

    for x in range(len(data)):
        ticker=data.iloc[x,0]
        tickerlist.append(ticker)
        tickerdate = data.iloc[x,1]
        tickerclose = data.iloc[x,2]
        tickerlist.append(ticker)
        b.setdefault(x,[]).append(ticker)
        b.setdefault(x,[]).append(str(tickerdate.date()))
        b.setdefault(x,[]).append(tickerclose)
    uniques = set(tickerlist)

    print("number of unuques= "+str(len(uniques)))
    print("first unuque= "+list(uniques)[0])
    return b
	
   # main_page = requests.get(url)
   # if search_term in keywords:
   #     return dict(get_keyword(search_term, main_page))
   # else:
   #     link = re.search(r'<option value="([^>]+)"> ' + search_term.capitalize() + ' </option>', main_page.text)
   #     if link:
   #        country_page = requests.get(url+link.group(1))
   #         return dict(get_country(country_page))
   #     else:
   #         return None
            
def get_keyword(search_term, main_page):
    """ Returns the data associated to the keyword 
    for each country as a list of tuple pairs. 
    :param search_term: keyword request.  
    :type search_term: str.
    :param main_page: the main Factbook page.
    :type main_page: Response obj.
    :returns: List of tuple pairs.
    :raises: None.
    """
    results = []
    keyword = keywords[search_term]
    link_pairs = re.findall(r'<option value="([^>]+)"> (.*?) </option>', main_page.text)
    for link, country in link_pairs:
        country_page = requests.get(url+link)
        data = get_country_by_keyword(country_page, keyword)
        results.append((country, data))
    return results

def get_country(country_page):
    """ Returns the data for the country as a list of tuple pairs. 
    :param country_page: The country's page on the Factbook.  
    :type country_page: Response obj.
    :returns: List of tuple pairs.
    :raises: None.
    """
    results = []    
    for keyword in keywords.values():
        data = get_country_by_keyword(country_page, keyword)     
        if data:
            results.append((keyword,data))
    return results

def get_country_by_keyword(country_page, keyword):
    """ Returns the data associated to the keyword 
    for the specific country. 
    :param country_page: The country's page on the Factbook.  
    :type country_page: Response obj.
    :param search_term: keyword request.  
    :type search_term: str.
    :returns: str.
    :raises: None.
    """
    if keyword == "Area" or keyword == "Capital":
        data = re.search(keyword + r":.*?<span class=category_data>(.+?)</span>", country_page.text, re.S)
        if data:
            return data.group(1)   
    elif keyword == "Exchange rates":
        data = re.search(keyword + r":.*?<div class=category_data>(.+?)</div>\n<div class=category_data>(.+?)</div>", country_page.text, re.S)
        if data:
            return data.group(1).rstrip(" -") + ": " + data.group(2)
    else:
        data = re.search(keyword + r":.*?<div class=category_data>(.+?)</div>", country_page.text, re.S)
        if data:
            return data.group(1)
    return None

   
if __name__ == "__main__":
	raw_entry = raw_input("Please enter a ticker symbol: ")
	search_term = raw_entry.split(" ")

    #return a pandas dataframe
	results = get_info_table(search_term)
	#get_info_json(search_term)
	
	
	print(results.get(0))
	for key,value in results.iteritems():
		print(value)
