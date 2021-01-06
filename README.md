# us-covid-stats
Web app that presents COVID-19 infection and death counts by U.S. ZipCodes (python, Flask, bootstrap).

Thanks to the [Mulesoft COVID-19 APIs](https://www.mulesoft.com/exchange/68ef9520-24e9-4cf2-b2f5-620025690913/covid19-data-tracking-api/)

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

## Building, Deploying & Running
This is a fairly straightfoward containerized application which can be run in several ways including locally via python, as a Docker container, or in Google Cloud Run.

** Run with Python **
From the root dir of the app:
`$ python app.py`

The app will be available on localhost port 8080 (e.g., http://0.0.0.0:8080)

** Dockerfile build/run **
From the root dir of the app:
`$ docker build -t covidweb . && docker run --rm -p 8080:8080 -e PORT=8080 covidweb`

The app will be available on localhost port 8080 (e.g., http://0.0.0.0:8080)

** Google Cloud Run (via Cloud Build) **
For something really cool, try clicking the *Run on Google Cloud* button above.
- OR -
From the root dir of the app:
`$ gcloud builds submit . --config=cloudbuild.yaml`

The build results will provide a unique URL for the app.

## Testing geolocation in dev
Geolocation is done by IP address (using [ip-api.com](https://ip-api.com)). When testing locally, your external IP will not be reported to the app, so 
set the `DEV_EXT_IP` in your dev environment or in the Dockerfile to your external IP for testing.
