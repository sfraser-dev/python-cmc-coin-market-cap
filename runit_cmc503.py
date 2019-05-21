#!/usr/bin/env python
# -*- coding: utf-8 -*-

# using Anaconda Python

# https://github.com/mrsmn/coinmarketcap-api
# https://pypi.python.org/pypi/forex-python (jumped from v0.3.3 to v1.0.0; new source "ratesapi.io")

import sys
import pprint
import smtplib
import datetime
import requests
from requests import Request, Session
import json
import pprint

# key to access my cmc account
cmc503_key= '2c6b43a8-fdf9-4305-b527-32555cd28db1'
# get crypto coin information as dictionary (specific url for crypto info)
cmc503_api_cryptos = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
cmc503_params = {
    'start': '1',
    'limit': '1000',
    'convert': 'USD',
}
cmc503_headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '2c6b43a8-fdf9-4305-b527-32555cd28db1',
}
# get global information as dictionary (specific url for global info)
cmc503_api_globs = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest?CMC_PRO_API_KEY='
cmc503_api_globs += cmc503_key

from forex_python.converter import CurrencyRates
myFx = CurrencyRates()

from email.mime.text import MIMEText

from optparse import OptionParser

def send_email (subject, body, to, pass_wd):
    sent_from = 'cmcwatcher@gmail.com'  
    email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login('cmcwatcher', pass_wd)
        server.sendmail(sent_from, to, email_text)
        server.close()
        print "email sent to: {}".format(to[0])
    except:
        print 'email failure!'

def cmc503_get_coin_data(coindict, bigdatadict, cable):
    #pprint.pprint(bigdatadict)
    #print("length of dictionary is: %d" %len(bigdatadict['data']))
    for ii in bigdatadict['data']:
        sslug = ii['slug']
        ssymbol = ii['symbol']
        #nname = ii['name']
        ppriceUSD = ii['quote']['USD']['price']
        ppriceGBP = ppriceUSD/cable
        cchange1hr = ii['quote']['USD']['percent_change_1h']
        cchange24hr = ii['quote']['USD']['percent_change_24h']
        cchange7d = ii['quote']['USD']['percent_change_7d']
        if (coindict['slug']==sslug):
            coindict['usd']=ppriceUSD
            coindict['gbp']=ppriceGBP
            coindict['curvalUsd']=ppriceUSD*coindict['abs']
            coindict['curvalGbp']=ppriceGBP*coindict['abs']
            coindict['1hr']=cchange1hr
            coindict['24hrs']=cchange24hr
            coindict['7days']=cchange7d
            #pprint.pprint(coindict)

def symbol_format(dic):
    # only want sybols of three letters
    sym = dic["symbol"]
    if sym == "miota":
        return "iot"
    else:
        return sym

def calc_roi_dict(dic):
#    if dic["symbol"] == "bch":
#        return 0.000
    try:
        roi = (dic["curvalGbp"]-dic["costBasisGbp"])/dic["costBasisGbp"]
    except ZeroDivisionError:
        roi = float('Inf')
    return roi*100

### main 
parser = OptionParser(usage='usage: %prog -p PASSWD')
parser.add_option("-p", dest="passwd",
                    help="PASSWD for email server", metavar="PASSWD")
(options, args) = parser.parse_args()
if not options.passwd:
   parser.error('email server passwd not given') 
   sys.exit(2)
passwd_cmcwatcher = options.passwd

# get gbp/usd
cable       = float(myFx.get_rate('GBP','USD'))
cable_rev   = float(myFx.get_rate('USD','GBP'))
chunnel     = float(myFx.get_rate('EUR','GBP'))
chunnel_rev = float(myFx.get_rate('GBP','EUR'))

# python 2.7 is ascii by default (ie: no GBP £ sign)
gbpUnicode = unichr(163)
gbpAscii = gbpUnicode.encode('utf-8')

# get date and time
now = datetime.datetime.now()
dateTime = now.strftime("%Y-%m-%d %H:%M")
email_body = "date and time: {}\n".format(dateTime)
email_body += "gbp/usd: {:.4f}\n".format(cable)
email_body += "gbp/eur: {:.4f}\n".format(chunnel_rev)
email_body += "usd/gbp: {:.4f}\n".format(cable_rev)
email_body += "eur/gbp: {:.4f}\n\n".format(chunnel)

# global data
cmc503_raw_data_globs = requests.get(cmc503_api_globs).json()
cmc503_data_globs = cmc503_raw_data_globs['data']
marketCap=cmc503_data_globs['quote']['USD']['total_market_cap']
marketVol=cmc503_data_globs['quote']['USD']['total_volume_24h']

email_body += "market cap = ${:10.2f}B = {:}{:10.2f}B\n".format(marketCap/1000000000, gbpAscii, (marketCap/1000000000)/cable)
email_body += "market vol = ${:10.2f}B = {:}{:10.2f}B (in the last 24h)\n".format(marketVol/1000000000, gbpAscii, (marketVol/1000000000)/cable)
email_body += "\n"

########################### add new coins here #################################
# cgt: cost basis for CGT calculation, T1 to T9 (note: two sells so two subtractions)
# cgt: selling X% of crypto reduces cost basis by X% (done by calculating BTC reserve cost basis and selling price)
# cgt: buying and selling at different times will adjust this percentage
cgtCostBasisForAllCryptoGbp = float(1698.84+2020.00+8509.00+5020.00-15147.52+8496.23+2300.00-4674.48)
# skin: T1-T6 profit of £598.42 summary + cost basis of subsequent tranches
# skin: absolute value of capital in minus capital out (getting in early gave large profits; my later trading gave losses)
# skin: this is why skin shows I have pulled out a profit and still have crypto, whereas cgt shows I still have a cost basis for the crypto
skinInTheGameGbp = float(598.42+8496.23+2300.00-12533.06)                                               

btcDict = { "slug":"bitcoin", 
            "symbol":"btc", 
            "abs":float(2.01278137-1.1130521), 
            "usd":float(0), 
            "gbp":float(0), 
            "curvalUsd":float(0), 
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float((229.02+2230.03)*(1-0.5530))}    # (T1-T6 + T7) multiplied by T9
ethDict = { "slug":"ethereum",
            "symbol":"eth",
            "abs":float(34.80491069-18.0814),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float((369.40+1847.85)*(1-0.5184))}    # (T1-T6 + T7) multiplied by T9
xmrDict = { "slug":"monero",
            "symbol":"xmr",
            "abs":float(25.87977261),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(1803.39+(1000+0))} # T7 + T8
xrpDict = { "slug":"ripple",
            "symbol":"xrp",
            "abs":float(626.349131),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(1300.00)}          # T8 
bchDict = { "slug":"bitcoin-cash",
            "symbol":"bch",
            "abs":float(1.52451799),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(0.00)}             # T7 (no cost, free from blockchain split)
neoDict = { "slug":"neo",
            "symbol":"neo",
            "abs":float(70.30806569),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(1064.50)}          # T7 
btgDict = { "slug":"bitcoin-gold",
            "symbol":"btg",
            "abs":float(1.71581177),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(0.00)}             # T8 (no cost, free from blockchain split)
gasDict = { "slug":"gas",
            "symbol":"gas",
            "abs":float(3.0585122),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(0.00)}             # T8 (no cost, free from neon wallet)
###############################################
bsvDict = { "slug":"bitcoin-sv",                        # UNCLAIMED: held BCH on ledger nano at the split, still need to claim BSV
            "symbol":"bsv",
            "abs":float(1.52451799),                    # UNCLAIMED BSV forked from BCH on 15 Nov 2018,
            "usd":float(0),                             # for each bitcoin-cash (BCH), got 1 BSV
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(0.00)}                 # UNCLAIMED (no cost, free from BCH split)
###############################################
sc6LossDictHardcode = { "slug":"",
            "symbol":"sc6",                             # HARDCODED: 6 small coins (sc6) that I lost money on in T7
            "abs":float(1),                             # (6 altcoins: omg, pay, bnb. bmt, lsk, iota)
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(1520.84+15.01+14.61)}  # HARDCODED
###############################################

# curly brace = dictionary/sets; square bracket = list/array
# a dictionary is returned; this dictionary contains various elements, some of which are lists of dictionaries!
# coin data
session = Session()
session.headers.update(cmc503_headers)
response = session.get(cmc503_api_cryptos, params=cmc503_params)
more100_data=json.loads(response.text)
cmc503_get_coin_data(btcDict, more100_data, cable)
cmc503_get_coin_data(ethDict, more100_data, cable)
cmc503_get_coin_data(xmrDict, more100_data, cable)
cmc503_get_coin_data(xrpDict, more100_data, cable)
cmc503_get_coin_data(bchDict, more100_data, cable)
cmc503_get_coin_data(neoDict, more100_data, cable)
cmc503_get_coin_data(btgDict, more100_data, cable)
cmc503_get_coin_data(gasDict, more100_data, cable)
cmc503_get_coin_data(bsvDict, more100_data, cable)
# HARDCODED -- cmc503_get_coin_data(sc6DictHardcode, more100_data, cable)

# create an array of crypto dictionaries (and the loss from sc6)
arr = [btcDict, ethDict, xmrDict, xrpDict, bchDict, neoDict, btgDict, gasDict, bsvDict, sc6LossDictHardcode]

totalUsd = float(0)
totalGbp = float(0)
# loop through the array of dictionaries, get spot prices of owned crypto
for x in arr:
    email_body += "{:} price = ${:10.2f} = {:}{:10.2f}, 1hr={:10.2f}%, 24hrs={:10.2f}%, 7days={:10.2f}%\n".format(symbol_format(x), x["usd"], gbpAscii, x["gbp"], x["1hr"], x["24hrs"], x["7days"])
    totalUsd += x["curvalUsd"]
    totalGbp += x["curvalGbp"]
email_body += "\n"
# loop through the array of dictionaries, get values of crypto coins owned
CBbtcEth  = float(0)
CBaltCoin = float(0)
PLbtcEth  = float(0)
PLaltCoin = float(0)
for x in arr:
    email_body += "totValOf {:7.2f} {:3} = ${:10.2f} = {:}{:10.2f} (costBasis: {:}{:10.2f}, p/l: {:}{:10.2f}, roi: {:10.2f}%, avgCostPerCoin: {:}{:10.2f} (${:10.2f}))\n".format(x["abs"],symbol_format(x),x["curvalUsd"],gbpAscii, x["curvalGbp"], gbpAscii, x["costBasisGbp"], gbpAscii, x["curvalGbp"]-x["costBasisGbp"], calc_roi_dict(x), gbpAscii, x["costBasisGbp"]/x["abs"], x["costBasisGbp"]/x["abs"]*cable)
    if x["symbol"] == "btc" or x["symbol"] == "eth":
        CBbtcEth += x["costBasisGbp"]
        PLbtcEth += x["curvalGbp"]-x["costBasisGbp"]
    else:
        CBaltCoin += x["costBasisGbp"]
        PLaltCoin += x["curvalGbp"]-x["costBasisGbp"]

# roi
email_body += "total cgt purchase cost = {:}{:10.2f} (calculated per tranche) (${:10.2f})\n".format(gbpAscii, cgtCostBasisForAllCryptoGbp, (cgtCostBasisForAllCryptoGbp*cable))
email_body += "total cgt value         = {:}{:10.2f} (calculated per tranche) (${:10.2f})\n".format(gbpAscii, totalGbp, (totalGbp*cable))
roi = ((totalGbp - cgtCostBasisForAllCryptoGbp) / cgtCostBasisForAllCryptoGbp) * 100
email_body += "total cgt p/l           = {:}{:10.2f} (calculated per tranche) (${:10.2f})\n".format(gbpAscii, totalGbp-cgtCostBasisForAllCryptoGbp, ((totalGbp-cgtCostBasisForAllCryptoGbp)*cable))
email_body += "total cgt roi           = {:10.2f}%\n".format(roi)
email_body += "skin in the game        = {:}{:10.2f} (${:10.2f})\n".format(gbpAscii, skinInTheGameGbp, (skinInTheGameGbp*cable))

# create email subject, print info (email body and subject) and send email
# add market cap and market volume information to email subject
email_subject = "cmc data: cap=${:.1f}B, vol=${:.1f}B".format(marketCap/1000000000, marketVol/1000000000)
# add values of crypto coins owned to email subject
for x in arr:
    email_subject += ", {}={:}{:.2f}".format(symbol_format(x), gbpAscii, x["gbp"])
print(email_body)
print(email_subject)
send_email(email_subject, email_body, ['cmcwatcher@gmail.com'], passwd_cmcwatcher)
send_email(email_subject, email_body, ['toepoke@hotmail.com'], passwd_cmcwatcher)
