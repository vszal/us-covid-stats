# Be sure to set the IPINFO_TOKEN and DEV_EXT_IP environmental variables before running
# See https://www.mulesoft.com/exchange/68ef9520-24e9-4cf2-b2f5-620025690913/covid19-data-tracking-api/

import os
import re
import requests
import ipinfo
import zipcodes
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    #if no zipcode in URL, guess based on geolocation
    ip_address = get_ip()
    zipcode, country = get_location_by_ip(ip_address)
    if country != 'US':
        return render_template('error.html', country=country)
    #query the NYT API    
    county, covid_data = get_covid_data(zipcode)
    return render_template('index.html', zipcode=zipcode, country=country, county=county, covid_data=covid_data)

@app.route('/<zipcode>')
def zip(zipcode):
    # Test if the inputted zipcode is real using the package "zipcodes"
    try:
        zipcodes.is_real(zipcode)
        #query the NYT API    
        county, covid_data = get_covid_data(zipcode)
        return render_template('index.html', zipcode=zipcode, county=county, covid_data=covid_data)
    except:
        #return "False: it's not real"
        return render_template('error.html', zipcode=zipcode)

def get_ip():
    # GCP Cloud Run needs X-Forwarded_For
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr) 
    # For dev testing, replace local ip with an external ip
    if (re.search('^192|^127|^172|^10\.', ip_address)):
        ip_address = os.environ.get('DEV_EXT_IP')
    # Get zip code from IP
    return ip_address

def get_location_by_ip(ip_address):
    #setup ipinfo hander
    # store your ipinfo token as an env variable
    handler = ipinfo.getHandler(os.environ.get('IPINFO_TOKEN'))
    details = handler.getDetails(ip_address)
    # return zipcode from details
    return details.postal, details.country

def get_covid_data(zipcode):
    try:
        loc = requests.get(f'https://localcoviddata.com/covid19/v1/cases/newYorkTimes?zipCode={zipcode}&daysInPast=7')
        loc.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    #success    
    json_loc = loc.json()
    county = json_loc["counties"][0]["countyName"]
    data = json_loc["counties"][0]["historicData"]
    # calculate deltas and add to an array
    n = len(data) - 2 # since we're doing deltas and i starts at zero
    i = 0
    covid_data = []
    
    #iterate through data set
    while i <= n:
        # postiive delta
        pos_delta = data[i]["positiveCt"] - data[(i+1)]["positiveCt"] 
        # death delta
        death_delta = data[i]["deathCt"] - data[i+1]["deathCt"] 
        d_list =[data[i]["date"],data[i]["positiveCt"],pos_delta,data[i]["deathCt"],death_delta]
        # list of lists
        covid_data.append(d_list)
        i += 1
    return county, covid_data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))