#!/usr/bin/env python

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
cable   = float(myFx.get_rate('GBP','USD'))
chunnel = float(myFx.get_rate('EUR','GBP'))

# get date and time
now = datetime.datetime.now()
dateTime = now.strftime("%Y-%m-%d %H:%M")
email_body = "date and time: {}\n".format(dateTime)
email_body += "gbp/usd: {:.4f}\n".format(cable)
email_body += "eur/gbp: {:.4f}\n\n".format(chunnel)

# curly brace = dictionary/sets; square bracket = list/array
# a string type is returned, not a list / dictionary (print type(myStats) or print type(btcUsd))
myStats = coinmarketcap.stats()
marketCap = float(get_market_cap(myStats))
marketVol = float(get_market_vol(myStats))
email_body += "market cap = ${:5.2f}B = {:5.2f}B gbp\n".format(marketCap/1000000000, (marketCap/1000000000)/cable)
email_body += "market vol = ${:5.2f}B = {:5.2f}B gbp (in the last 24h)\n".format(marketVol/1000000000, (marketVol/1000000000)/cable)
email_body += "\n"

########################### add new coins here #################################
amountPaidForAllCryptoGbp = float(598.42+3030+1400)
btcDict = { "ticker":"bitcoin", 
            "symbol":"btc", 
            "abs":float(1.44733267), 
            "usd":float(0), 
            "gbp":float(0), 
            "curvalUsd":float(0), 
            "curvalGbp":float(0)}
ethDict = { "ticker":"ethereum",
            "symbol":"eth",
            "abs":float(26.9778444698),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0)}
bchDict = { "ticker":"bitcoin-cash",
            "symbol":"bch",
            "abs":float(1.52451799),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0)}
neoDict = { "ticker":"neo",
            "symbol":"neo",
            "abs":float(69.53306569),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0)}
omgDict = { "ticker":"omisego",
            "symbol":"omg",
            "abs":float(171.546878),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0)}
tnxDict = { "ticker":"tenx",
            "symbol":"pay",
            "abs":float(172.10421034),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0)}
bnbDict = { "ticker":"binance-coin",
            "symbol":"bnb",
            "abs":float(547),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0)}
bmtDict = { "ticker":"bytom",
            "symbol":"bmt",
            "abs":float(2500),
            "usd":float(0),
            "gbp":float(0),
            "curvalUsd":float(0),
            "curvalGbp":float(0)}
get_price_from_cmc(btcDict, cable)
get_price_from_cmc(ethDict, cable)
get_price_from_cmc(bchDict, cable)
get_price_from_cmc(neoDict, cable)
get_price_from_cmc(omgDict, cable)
get_price_from_cmc(tnxDict, cable)
get_price_from_cmc(bnbDict, cable)
get_price_from_cmc(bmtDict, cable)
# create an array of crypto dictionaries
arr = [btcDict, ethDict, bchDict, neoDict, omgDict, tnxDict, bnbDict, bmtDict]

totalUsd = float(0)
totalGbp = float(0)
# loop through the array of dictionaries, get spot prices of owned crypto
for x in arr:
    email_body += "{:5} price = ${:7.2f} = {:7.2f} gbp\n".format(x["symbol"], x["usd"], x["gbp"])
    totalUsd += x["curvalUsd"]
    totalGbp += x["curvalGbp"]
email_body += "\n"
# loop through the array of dictionaries, get values of crypto coins owned
for x in arr:
    email_body += "total value of {:9.2f} {:6} = ${:8.2f} = {:8.2f} gbp\n".format(x["abs"],x["symbol"],x["curvalUsd"],x["curvalGbp"])
email_body += "{} = ${:8.2f} = {:8.2f} gbp\n".format("total overall value", totalUsd, totalGbp)
email_body += "\n"

# roi
roi = ((totalGbp - amountPaidForAllCryptoGbp) / amountPaidForAllCryptoGbp) * 100
email_body += "purchase cost = {:.2f} gbp\nroi = {:.1f}%\n".format(amountPaidForAllCryptoGbp, roi)

# create email subject, print info (email body and subject) and send email
# add market cap and market volume information to email subject
email_subject = "cmc data: cap=${:.1f}b, vol=${:.1f}b".format(marketCap/1000000000, marketVol/1000000000)
# add values of crypto coins owned to email subject
for x in arr:
    email_subject += ", {}={:.1f}gbp".format(x["symbol"],x["gbp"])
print(email_body)
print(email_subject)
send_email(email_subject, email_body, ['cmcwatcher@gmail.com'], passwd_cmcwatcher)
#send_email(email_subject, email_body, ['toepoke@hotmail.com'], passwd_cmcwatcher)
