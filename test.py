import os
import re
import requests
import ipinfo
import zipcodes
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    ip_address=""
    try:
        loc_api = requests.get(f'http://ip-api.com/json/{ip_address}')
        loc_api.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    loc_data = loc_api.json()
    zipcode = loc_data['zip']
    country = loc_data['countryCode']
    return f'The zip is {zipcode}. Coutry is {country}'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
