import os
import re
import requests
import zipcodes
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    #if no zipcode in URL, guess based on geolocation
    ip_address = get_ip()
    if ip_address =='': #ip_address is undefined, likely missing environment variable
        return '<strong>IP address is undefined. Make sure DEV_EXT_IP environment variable is set</strong>'
    else:
        zipcode, country = get_location_by_ip(ip_address)
        if country != 'US':
            return render_template('error.html', country=country)
        #query the covid data API    
        county, lat, lng, covid_data = get_covid_data(zipcode)
        return render_template('index.html', zipcode=zipcode, country=country, county=county, lat=lat, lng=lng, covid_data=covid_data)        

@app.route('/<zipcode>')
def zip(zipcode):
    # Test if the inputted zipcode is real using the package "zipcodes"
    try:
        zipcodes.is_real(zipcode)
    except:
        return render_template('error.html', zipcode=zipcode)
    #query the covid data and population APIs    
    county, lat, lng, covid_data = get_covid_data(zipcode)
    return render_template('index.html', zipcode=zipcode, county=county, lat=lat, lng=lng, covid_data=covid_data)

def get_ip():
    # GCP Cloud Run needs X-Forwarded_For
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr) 
    # For dev testing, get external IP from environment variable
    if (re.search('^192|^127|^172|^10\.', ip_address)):
        ip_address = os.environ.get('DEV_EXT_IP')  
    return ip_address

def get_location_by_ip(ip_address):
    try:
        loc_api = requests.get(f'http://ip-api.com/json/{ip_address}')
        loc_api.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    loc_data = loc_api.json()
    zipcode = loc_data['zip']
    country = loc_data['countryCode']
    return zipcode, country

def get_covid_data(zipcode):
    try:
        covid_api = requests.get(f'https://localcoviddata.com/covid19/v1/cases/newYorkTimes?zipCode={zipcode}&daysInPast=7')
        covid_api.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    cov_data = covid_api.json()
    county = cov_data["counties"][0]["countyName"]
    lat = cov_data["counties"][0]["geo"]["leftBottomLatLong"]
    lng = cov_data["counties"][0]["geo"]["rightTopLatLong"]
    data = cov_data["counties"][0]["historicData"]
    # get population for county by coordinates
    county_population = get_census_data(lat, lng)
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
        pos_per_1000 = "{:.2f}".format(data[i]["positiveCt"]/(county_population/1000))
        death_per_1000 = "{:.2f}".format(data[i]["deathCt"]/(county_population/1000))
        d_list =[data[i]["date"],data[i]["positiveCt"],pos_delta,data[i]["deathCt"],death_delta, pos_per_1000, death_per_1000]
        # list of lists
        covid_data.append(d_list)
        i += 1
    return county, lat, lng, covid_data

def get_census_data(lat, lng):
    # the census API requires queries via FIPS geocodes, which we get via this coordinates query
    # see https://geo.fcc.gov/api/census/
    try:
        geocode = requests.get(f'https://geo.fcc.gov/api/census/block/find?latitude={lat}&longitude={lng}&showall=true&format=json')
        geocode.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err) 

    geocodej = geocode.json()
    FIPS_code = geocodej["County"]["FIPS"]
    state_code = FIPS_code[0:2]
    county_code = FIPS_code[2:5]
    
    # get county population from the census API
    try:
        population = requests.get(f'https://api.census.gov/data/2019/pep/population?get=POP,NAME,STATE&for=county:{county_code}&in=state:{state_code}')
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err) 

    popj = population.json()
    county_population = int(popj[1][0])
    return county_population

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))