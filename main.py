from contextlib import asynccontextmanager
from fastapi import FastAPI
from decouple import config
from fastapi.middleware.cors import CORSMiddleware

import requests
import json

LOCATION = config("LOCATION")
OUTPUT_DICT = {}
NEXT_LINK = "https://www.goodgym.org/api/openactive/events"

def get_data():
    global NEXT_LINK

    input_list = []
    data_items = "initialised"
    while data_items:

        print(f"Getting data from {NEXT_LINK}")

        # get data from GoodGym endpoint
        response = requests.get(NEXT_LINK)
        data_json = response.json()

        # extract event data and next link
        data_items = data_json["items"]
        NEXT_LINK = data_json["next"]

        if data_items:
            # put the items data in a dict
            items_string = json.dumps(data_items)
            input_dict = json.loads(items_string)

            input_list.extend([[x["modified"], x] for x in input_dict])

    # order the data by "modified" so we can process in correct order
    sorted(input_list, key=lambda l:l[0])

    for modified, x in input_list:
        if "data" in x and (x["data"]["location"]["address"]["addressLocality"] == LOCATION):
            OUTPUT_DICT[x["id"]] = x
            print(f"UPDATE ID: {x["id"]} ({x["data"]["name"]})")
        elif x["state"] == "deleted":
            print(f"DELETE ID: {x["id"]}")
            OUTPUT_DICT.pop(x["id"], None)

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_data()
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
    
    # update the data using next link
    get_data()
    
    # create events list
    events_list = [ x for x in OUTPUT_DICT.values() ]
    events_list.sort(key=lambda event: event["data"]["startDate"])

    # create list of locations
    locations = []
    group_run_added = False
    location_number = 0
    for event in events_list:
        event_type = event["data"]["programme"]["name"]
        if event_type == "Group Run":
            if group_run_added:
                continue
            name = "Group Run/Walk"
            background = "#e11018"
            group_run_added = True

            latitude = 51.45110
            longitude = -2.5926500
        else:
            if event_type == "Community Mission":
                name = event["data"]["name"]
                background = "#d66c20"
            elif event_type == "Party":
                name = event["data"]["name"]
                background = "#b176db"
            elif event_type == "Race":
                name = event["data"]["name"]
                background = "#639be6"
            elif event_type == "Training Session":
                name = event["data"]["name"]
                background = "#88c77b"
            else:
                name = event["data"]["name"]
                background = "white"
            
            latitude = event["data"]["location"]["geo"]["latitude"]
            longitude = event["data"]["location"]["geo"]["longitude"]
        
        locations.append(
                {
                    "number": location_number,
                    "name": name, 
                    "position": {
                        "lat": latitude, 
                        "lng": longitude
                    },
                    "background": background
                }
            )
        location_number += 1

    return {"events": events_list, "locations": locations}