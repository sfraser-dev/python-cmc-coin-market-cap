#!/usr/bin/env python                                                                                                                            
# -*- coding: utf-8 -*-

# https://towardsdatascience.com/cryptocurrency-data-analysis-in-python-using-rest-api-8c28234e5fd

import requests
from prettytable import PrettyTable

key = '2c6b43a8-fdf9-4305-b527-32555cd28db1'
api = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?CMC_PRO_API_KEY='
api += key

raw_data = requests.get(api).json()
data = raw_data['data']

table = PrettyTable()

for currency in data:
    name = currency['name']
    price = currency['quote']['USD']['price']
    market_cap = currency['quote']['USD']['market_cap']
    change_1h = currency['quote']['USD']['percent_change_1h']
    change_24h = currency['quote']['USD']['percent_change_24h']
    change_7d = currency['quote']['USD']['percent_change_7d']

    table.add_row([name,price,market_cap,change_1h,change_24h,change_7d])

table.field_names = ["Name","Price","Market Cap", "Change 1h","Change 24h","Change 7d"]
table.sortby = "Market Cap"
table.reversesort = True
print(table)

