# README

## Introduction

Using the GoodGym data described at https://github.com/good-gym/opendata, get upcoming events for a location.

Gets future event data from GoodGym for the location LOCATION (environment variable) and exposes it in a [FastAPI](https://fastapi.tiangolo.com/) endpoint to be consumed by a front end. The initial data load is done during startup then the idea will be that whenever we hit the endpoint we get any updates to the data and add it before returning.

Setup to deploy to [Render](https://render.com/docs/deploy-fastapi).

A front end is being worked on here:
https://github.com/richardgiddings/goodgym-events-frontend

## To install and run

To start with you need python installed, then...

Best to install the dependencies in a virtual environment, e.g.
```
python -m venv goodgym-env
source goodgym-env/bin/activate
```
Install the dependencies with:
```
pip install -r requirements.txt
```
Then run FastAPI (locally) with:
```
fastapi dev main.py
```
Hit the endpoint with:
```
http://127.0.0.1:8000/events/
```
(Note the location in a .env file or environment variable determines the location data is returned for)

## Links

- [Consuming data](https://developer.openactive.io/using-data/harvesting-opportunity-data-1)
- [GoodGym GitHub Repo](https://github.com/good-gym/opendata)
- [OpenActive Specification](https://openactive.io/realtime-paged-data-exchange/)

## Changes Needed

- At the moment it only gets the first page of data but its unclear how the next link works at the moment to get subsequent data. [This](https://openactive.io/realtime-paged-data-exchange/#:~:text=4.3.1%20Modified%20Timestamp%20and%20ID) is how the next data should work I believe. 