from contextlib import asynccontextmanager
from fastapi import FastAPI
from decouple import config
from fastapi.middleware.cors import CORSMiddleware

import requests
import json

LOCATION = config("LOCATION")
OUTPUT_DICT = {}
NEXT_LINK = ""

def load_data():
    NEXT_LINK = "https://www.goodgym.org/api/openactive/events"

    # get data from GoodGym endpoint
    response = requests.get(NEXT_LINK)
    data_json = response.json()

    # extract event data and next link
    data_items = data_json["items"]
    NEXT_LINK = data_json["next"]

    # put the items data in a dict
    items_string = json.dumps(data_items)
    input_dict = json.loads(items_string)

    # order the data by "modified" so we can process in correct order
    input_list = [[x["modified"], x] for x in input_dict]
    sorted(input_list, key=lambda l:l[0])

    # now process the data
    for modified, x in input_list:
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

# CORS middleware
ALLOWED_ORIGINS = config("ALLOWED_ORIGINS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # set this once we are no longer testing locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Nothing to see here!"}

@app.get("/events/")
def read_events():
    return {"events": [ x for x in OUTPUT_DICT.values() ]}