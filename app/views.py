from flask import render_template, make_response, jsonify, request
from app import t_app
from app.forms import CountrySearch
from app.symbol_scraper import get_info, get_info_table, graph



import random
import pandas
import urllib


@t_app.route('/')
@t_app.route('/index')
def index():
    return render_template('index.html')

@t_app.route('/search', methods=['GET', 'POST'])
def search():
    #info = None
    global png_output, ticker, globalvar
    png_output=""
    b = {}
    list_values=[]
    temp=[]
    data=pandas.DataFrame()
    form = CountrySearch()
    if form.validate_on_submit():
        ticker = form.country_name.data
        globalvar=ticker
        for x in ticker:
            print ticker
		
        #return a dictionary
        info = get_info_table(ticker)
        print str(len(info))

        #add the values to tmp list
        for key, value in info.iteritems():
            temp.append(value)
        print len(temp)

        #get data for the ticker in list
        data=get_info(globalvar)

        print(str(len(data)))

        png_output=graph(data)

    
    return render_template('search.html', title='Search for a stock', form=form, info=temp,img_data=urllib.quote(png_output.rstrip('\n')) )

