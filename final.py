from __future__ import print_function
import argparse
import pprint
import requests
import sys
import urllib
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
import sqlite3
import csv
import re
import requests
import json
from bs4 import BeautifulSoup
import urllib

from secrets import *




API_KEY= None 
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.



DEFAULT_TERM = 'restaurants'
DEFAULT_LOCATION = 'Ann Arbor, MI'
SEARCH_LIMIT = 50



def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()



def search(api_key, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)



def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(API_KEY, term, location)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return

    business_id = businesses[0]['id']

    print(u'{0} businesses found, querying business info ' \
        'for the top result "{1}" ...'.format(
            len(businesses), business_id))
    response = get_business(API_KEY, business_id)

    print(u'Result for business "{0}" found:'.format(business_id))
    pprint.pprint(response, indent=2)


def get_business(api_key, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)



class foodiecity():
    def __init__(self,latitude,longtude,place_id):
        self.place_id = place_id
        self.latitude= latitude
        self.longtude = longtude

class Hotelsinfor():
    def __init__(self,hotel_number,hotels,hotel_latitude,hotel_longtude):
        self.hotel_number = hotel_number
        self.hotels = hotels
        self.hotel_latitude= hotel_latitude
        self.hotel_longtude = hotel_longtude


class Thingstodoinfor():
    def __init__(self,things_to_do_number,things_to_do,things_to_do_latitude,things_to_do_longtide):


class Restinfor():
    def __init__(self,rest_number,rest_id,rest_alias,rest_name,rest_image_url,rest_is_closed,rest_url,rest_review_count,rest_rating,rest_location,rest_phone,rest_distance):
        self.rest_number = rest_number
