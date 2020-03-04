import requests
import json
from decimal import *
import boto3
import datetime

URL = "https://api.yelp.com/v3/businesses/search"
count = 0
with open('../data/restaurants_american.json', 'w') as f:
    final_businesses = []
    for i in range(0, 1000, 50):
        # location given here
        term = "Restaurants"
        location = "Manhattan"
        limit = 50
        categories = "american"
        offset = i
        headers = {'Authorization': 'Bearer a_M9Y7_e_URva_rVnSvPugh_wMgmZNPMnowiQ_nIV9t9MuE_W7O8gBr7sm0agIx-OHqjVDLa8sLCM1F3TTw7hSvGCIKHsjBGOL71cBfpMcR2HCQZjMOgUe5UpFRdXnYx'}
        # defining a params dict for the parameters to be sent to the API
        PARAMS = {'term': term,'categories': categories, 'location': location, 'limit':limit, 'offset':offset }

        # sending get request and saving the response as response object
        r = requests.get(url=URL,headers=headers, params=PARAMS)

        # extracting data in json formats
        data = r.json()

        for dic in data['businesses']:
            final_businesses.append(dic)
            count += 1
    final_businesses = json.dumps(final_businesses, indent=4, separators=(',',':'))
    f.write(final_businesses)
print(count)
