from contextlib import asynccontextmanager
from fastapi import FastAPI
from decouple import config

import requests
import json

LOCATION = config("LOCATION")
OUTPUT_DICT = {}

def load_data():
    response = requests.get('https://www.goodgym.org/api/openactive/events')
    data_json = response.json()
    data_items = data_json["items"]
    data_string = json.dumps(data_items)
    input_dict = json.loads(data_string)

    for x in input_dict:
        if "data" in x and (x["data"]["location"]["address"]["addressLocality"] == LOCATION):
            OUTPUT_DICT[x["id"]] = x
        elif x["state"] == "deleted":
            OUTPUT_DICT.pop(x["id"], None)

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data()
    yield
    OUTPUT_DICT.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Nothing to see here!"}

@app.get("/events/")
def read_events():
    return OUTPUT_DICT