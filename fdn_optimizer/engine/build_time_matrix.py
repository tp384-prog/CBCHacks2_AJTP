# engine/build_time_matrix.py
import requests
import os
from dotenv import load_dotenv  # ADD THIS
load_dotenv() 

def build_time_matrix(donations, pantries):
    locations = [d["location"] for d in donations] + \
                [p["location"] for p in pantries]

    # ORS expects [lng, lat] not [lat, lng]
    coords = [[loc[1], loc[0]] for loc in locations]

    response = requests.post(
        "https://api.openrouteservice.org/v2/matrix/driving-car",
        headers={ "Authorization": os.getenv("ORS_API_KEY") },
        json={ "locations": coords }
    )

    data = response.json()
    return data["durations"]  # pairwise matrix in seconds

