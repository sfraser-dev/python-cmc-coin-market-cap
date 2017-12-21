#!/usr/bin/env python
# -*- coding: utf-8 -*-

# using Anaconda Python

# https://github.com/mrsmn/coinmarketcap-api
# https://pypi.python.org/pypi/forex-python

import sys
import pprint
import smtplib
import datetime

from coinmarketcap import Market
coinmarketcap = Market()

from forex_python.converter import CurrencyRates
myFx = CurrencyRates()

from email.mime.text import MIMEText

from optparse import OptionParser

def get_values_as_dict (longstring):
    myDict = {}
    # the coin info from coinmarket cap is a single long string
    for line in longstring.splitlines():
        if "[" not in line:
            if "{" not in line:
                if "}" not in line:
                    if "]" not in line:
                        # remove leading white space
                        noWhite = line.lstrip(' ')
                        noQuotes = noWhite.replace('"', '')
                        sp = noQuotes.split(":")
                        # remove leading white space
                        left = sp[0].lstrip(' ');
                        right = sp[1].lstrip(' ');
                        # remove commas
                        left = left.replace(',', '')
                        right = right.replace(',', '')
                        ## store in dictionary what is "left" and "right" of the equals sign
                        myDict[left] = right
    return myDict

def get_price_usd (longstring):
    myDict = get_values_as_dict(longstring)
    for key, value in myDict.items():
        if "price_usd" in key:
            return value

def get_change_1hr (longstring):
    myDict = get_values_as_dict(longstring)
    for key, value in myDict.items():
        if "percent_change_1h" in key:
            return value

def get_change_24hrs (longstring):
    myDict = get_values_as_dict(longstring)
    for key, value in myDict.items():
        if "percent_change_24h" in key:
            return value

def get_change_7days (longstring):
    myDict = get_values_as_dict(longstring)
    for key, value in myDict.items():
        if "percent_change_7d" in key:
            return value

def get_market_vol (longstring):
    myDict = get_values_as_dict(longstring)
    for key, value in myDict.items():
        if "total_24h_volume_usd" in key:
            return value

def get_market_cap (longstring):
    myDict = get_values_as_dict(longstring)
    for key, value in myDict.items():
        if "total_market_cap_usd" in key:
            return value

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

def get_price_from_cmc(dic, cable):
    usd = float(get_price_usd(coinmarketcap.ticker(dic['ticker'])))
    gbp = float(usd/cable)
    dic['usd']=usd
    dic['gbp']=gbp
    dic["curvalUsd"]=dic["abs"]*usd
    dic["curvalGbp"]=dic["abs"]*gbp
    dic["1hr"]=float(get_change_1hr(coinmarketcap.ticker(dic['ticker'])))
    dic["24hrs"]=float(get_change_24hrs(coinmarketcap.ticker(dic['ticker'])))
    dic["7days"]=float(get_change_7days(coinmarketcap.ticker(dic['ticker'])))

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

#allCoins = coinmarketcap.ticker()
#print allCoins

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

# curly brace = dictionary/sets; square bracket = list/array
# a string type is returned, not a list / dictionary (print type(myStats) or print type(btcUsd))
myStats = coinmarketcap.stats()
marketCap = float(get_market_cap(myStats))
marketVol = float(get_market_vol(myStats))
email_body += "market cap = ${:10.2f}B = {:}{:10.2f}B\n".format(marketCap/1000000000, gbpAscii, (marketCap/1000000000)/cable)
email_body += "market vol = ${:10.2f}B = {:}{:10.2f}B (in the last 24h)\n".format(marketVol/1000000000, gbpAscii, (marketVol/1000000000)/cable)
email_body += "\n"

########################### add new coins here #################################
amountPaidForAllCryptoGbp = float( (598.42+3030+(2520-1150.39+67)) + (1000+15.01+3000+14.61))     # T1-T6 + T7
amountPaidForAllCryptoGbp += float((1000+0))        # T8

btcDict = { "ticker":"bitcoin", 
            "symbol":"btc", 
            "abs":float(2.01278971), 
            "usd":float(0), 
            "gbp":float(0), 
            "curvalUsd":float(0), 
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(229.02+2230.03)}    # T1-T6 + T7
ethDict = { "ticker":"ethereum",
            "symbol":"eth",
            "abs":float(34.80491069),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(369.40+1847.85)}    # T1-T6 + T7
xmrDict = { "ticker":"monero",
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
bchDict = { "ticker":"bitcoin-cash",
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
btgDict = { "ticker":"bitcoin-gold",
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
neoDict = { "ticker":"neo",
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
###############################################
sc6LossDictHardcode = { "ticker":"",
            "symbol":"sc6",
            "abs":float(1),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0),
            "1hr":float(0),
            "24hrs":float(0),
            "7days":float(0),
            "costBasisGbp":float(1520.84+15.01+14.61)}      # 6 small coins (sc6) that I lost money on in T7 (6 altcoins: omg, pay, bnb. bmt, lsk, iota)
###############################################
get_price_from_cmc(btcDict, cable)
get_price_from_cmc(ethDict, cable)
get_price_from_cmc(xmrDict, cable)
get_price_from_cmc(bchDict, cable)
get_price_from_cmc(btgDict, cable)
get_price_from_cmc(neoDict, cable)
# HARDCODED -- get_price_from_cmc(sc6DictHardcode, cable)
# create an array of crypto dictionaries (and the loss from sc6)
arr = [btcDict, ethDict, xmrDict, bchDict, btgDict, neoDict, sc6LossDictHardcode]

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
email_body += "total overall purchase cost = {:}{:10.2f} (calculated per tranche)\n".format(gbpAscii, amountPaidForAllCryptoGbp)
email_body += "total overall value         = {:}{:10.2f} (calculated per tranche)\n".format(gbpAscii, totalGbp)
roi = ((totalGbp - amountPaidForAllCryptoGbp) / amountPaidForAllCryptoGbp) * 100
email_body += "total overall p/l           = {:}{:10.2f} (calculated per tranche)\n".format(gbpAscii, totalGbp-amountPaidForAllCryptoGbp)
email_body += "total overall roi = {:10.2f}%\n".format(roi)

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
