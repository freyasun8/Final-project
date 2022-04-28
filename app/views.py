
from app import app

import requests
import json
from flask import render_template
from flask import request as rq
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
import re
import os
import argparse
import time
parser = argparse.ArgumentParser()
parser.add_argument("-link")
args = parser.parse_args()
import argparse
import json
import pprint
import requests
import sys
import string
import urllib

from lxml import html


# Yelp API urls and constants

API_HOST = 'https://api.yelp.com'
WEBSITE_HOST = 'https://www.yelp.com/biz/'
SEARCH_PATH = '/v3/businesses/search'
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'
USER_AGENT = 'Mozilla/5.0'
TOKEN = 'fXEkoMvITNK3ZwPCtw0s-uvm_zpILlkn19Njzzy7X7MNMCG4QI9ATTNFwzI4accXrW1lH8a_w7mGJqbJWEeYd81oHIfyfssEFDt67kjZYcSmZBERCOc3CnLiCbllYnYx'
PATTERN = re.compile('[^a-zA-Z0-9 ]+')
LOCATION = 'Ann Arbor'
CATEGORY = 'Asian Fusion'
SEARCH_LIMIT = 10


#function to scrape reviews from Yelp's website
def get_reviews(bisID, n_revs):
    # scrape the business Yelp url
    url = '{0}{1}'.format(WEBSITE_HOST, bisID)
    url_params = {
        'start': 0,
        'sort_by': 'date_desc'
    }
    headers = {
        'user-agent': USER_AGENT
    }

    response = requests.get(url,headers=headers, params=url_params)
    soup = BeautifulSoup(response.text, 'html.parser')

    
    reviewsRaw = soup.find_all('script',type='application/ld+json')

    
    """if len(reviewsRaw) != 1:
        raise('Error scraping Yelp\'s webpage')
        """

    #tranform to dict and get all needed data
    reviewsDict = json.loads(reviewsRaw[0].string)
    result = {
        'name': reviewsDict['name'],
        'address': '%s, %s, %s %s' %(reviewsDict['address']['streetAddress'],
                                reviewsDict['address']['addressLocality'],
                                reviewsDict['address']['addressRegion'],
                                reviewsDict['address']['postalCode']),
        'rating': reviewsDict['aggregateRating']['ratingValue'],
        'reviews': reviewsDict['aggregateRating']['reviewCount'],
        'disp_reviews': n_revs,
        'url': url
    }

    reviews = [{
               'date': reviewsDict['review'][i]['datePublished'],
               'rating': reviewsDict['review'][i]['reviewRating']['ratingValue'],
               'description': reviewsDict['review'][i]['description']
               } for i in range(n_revs)]

    return result, reviews



    


# index page where user inputs query
@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

# search page that dynamically changes depending on results
@app.route('/search', methods=['GET','POST'])
def search():
    # two types of methods for the page:
    
    # if POST, then we get the result afterwards

    if rq.method == 'POST':
        # get the form
        search_term = rq.form["searchBox"]
        n_revs = int(rq.form["numRevs"])
        search_term_regex = PATTERN.sub('',search_term.lower())
        url = '{0}{1}'.format(API_HOST, SEARCH_PATH)
        url_params = {
            'term': search_term_regex,
            'location': LOCATION,
            'limit': SEARCH_LIMIT,
            'categories': CATEGORY,
        }
        headers = {
            'user-agent': USER_AGENT,
            'Authorization': 'Bearer %s' % TOKEN
        }
        response = requests.get(url,headers=headers, params=url_params)

        #if search doesnt return results, return to the search page 
        if len(response.json()) < 1:
            return render_template("search.html", search_term = search_term)

        #else: find strings that are most similar to query
        else:
            search_results = [PATTERN.sub('',bis['name'].lower()) for bis in response.json()['businesses']]
            n_results = len(search_results)
            search_scores = process.extract(search_term, search_results, limit=4, scorer=fuzz.token_set_ratio)

            if search_scores[0][1] > 90:
                if n_results > 1 and search_scores[1][1] > 90:
                    idx = search_results.index(search_scores[0][0])
                    idxset = [search_results.index(m[0]) for m in search_scores[1:] if m[1]>90]
                else:
                    idx = search_results.index(search_scores[0][0])
                    idxset = []
            
            elif search_scores[0][1] > 75:
                if n_results == 1 or (n_results > 1 and search_scores[1][1] < 50):
                    idx = search_results.index(search_scores[0][0])
                    idxset = []

                else:
                    idx = search_results.index(search_scores[0][0])
                    idxSet = [search_results.index(m[0]) for m in search_scores[1:] if m[1]>50]
            
            else:

                idx = None
                idxset = [search_results.index(m[0]) for m in search_scores if m[1]>50]

            if idx is not None:

                bisID = response.json()['businesses'][idx]['id']
                result, reviews = get_reviews(bisID, n_revs)

            else:
                result = {}
                reviews = []
            
            if idxset:
                suggestions = [{
                           'name': response.json()['businesses'][i]['name'],
                           'link': '/search?id=%s&n=%d' % (response.json()['businesses'][i]['id'], num_revs)
                           } for i in idxset]

            else:
                suggestions = []
            return render_template("search.html", result = result, reviews = reviews, search_term = search_term, suggestions = suggestions) # return html page
            
            
    

    elif rq.method == 'GET':
        bisID = rq.args.get('id')
        num_revs = rq.args.get('n', 1, type=int)
        result, reviews = get_reviews(bisID, num_revs)
        return render_template("search.html", result = result, reviews = reviews)

    
        
