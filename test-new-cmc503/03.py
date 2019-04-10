#!/usr/bin/env python                                                                                                                            
# -*- coding: utf-8 -*-

import time, requests, json
import datetime as dt

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC&convert=USD'

headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'deflate, gzip',
    'X-CMC_BASIC_API_KEY': '2c6b43a8-fdf9-4305-b527-32555cd28db1',
}

r = requests.get(url, headers=headers)

if r.status_code == 200:
    response = json.loads(r.text)
