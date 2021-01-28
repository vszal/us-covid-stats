# us-covid-stats

Web dashboard app that presents COVID-19 infection and death counts by U.S. county, search interface via ZipCode. Written in Python using Flask, javascript, bootstrap CSS.

Uses the [Mulesoft COVID-19 APIs](https://www.mulesoft.com/exchange/68ef9520-24e9-4cf2-b2f5-620025690913/covid19-data-tracking-api/). Note there are some known problems with this API at time of writing. For instance, it returns no data for zipcodes in NYC (e.g. 10001, 10005).

Population data gathered from the U.S. Census Bureau [Population Estimate API](https://www.census.gov/data/developers/data-sets/popest-popproj/popest.html).

## Building, Deploying & Running
This is a straightfoward Python Flask application which can be run in several ways including locally via python, as a Docker container, or in Google Cloud Run.

### via Python

From the root dir of the app:

`$ python app.py`

The app will be available on localhost port 8080 (e.g., `http://0.0.0.0:8080`)

### via Dockerfile

From the root dir of the app:

`$ docker build -t uscovidstats . && docker run --rm -p 8080:8080 -e PORT=8080 uscovidstats`

The app will be available on localhost port 8080 (e.g., `http://0.0.0.0:8080`)

### via Google Cloud Run (via Cloud Build)

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

\- OR -

From the root dir of the app:

`$ gcloud builds submit . --config=cloudbuild.yaml`

The build results will provide a unique URL for the app.

## Testing geolocation in dev
Geolocation is done by IP address (using [ip-api.com](https://ip-api.com)). When testing locally, your external IP may not be reported to the app, so set the `DEV_EXT_IP` to your external IP address in your dev environment or in the Dockerfile.

## Contributing
This is my first github project so feel free to submit recommendations via PR, or shoot me a message.
This project is not affiliated or sponsored by Alphabet or Google.
