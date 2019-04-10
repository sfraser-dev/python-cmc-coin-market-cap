#!/usr/bin/env python                                                                                                                            
# -*- coding: utf-8 -*-

# https://coinmarketcap.com/api/documentation/v1/#section/Quick-Start-Guide

# This example uses Python 2.7+ and the python-request library
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
    'start': '1',
    'limit': '5000',
    'convert': 'USD',
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '2c6b43a8-fdf9-4305-b527-32555cd28db1',
}

session = Session()
session.headers.update(headers)


try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    print(data)
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
