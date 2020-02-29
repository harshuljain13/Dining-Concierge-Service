import requests
import json
import os

def main():
    api_key = 'ucTJwlkUtHfkwSxf0JU93ukhwc8AC0fj8eRrRp0qhE9W35-hIeNvAkfX1mMb-K_PzeP47ZPLwBPrCViASlcHcgYiAKKSh3X2ZH4BLbp-YZRicg9Su8Z1uBd3He5ZXnYx'
    headers = {'Authorization': 'Bearer %s' % api_key}
    url='https://api.yelp.com/v3/businesses/search'
    params = {'term': 'restaurants', 'location':'california', 'offset':0, 'limit':50}
    
    final_businesses=[]
    while params['offset']<951:
        req=requests.get(url, params=params, headers=headers)
        print('Total restaurants: {}'.format(params['offset']+50))
        params['offset']+=50
        data = json.loads(req.text)
        businesses = data['businesses']

        final_businesses.extend(businesses)
        if len(businesses)<50:
            break
    print('number of restaurants are {}'.format(len(final_businesses)))
    with open('../data/ca_restaurants.json', 'w') as f:
        f.write(json.dumps({'businesses': final_businesses}, indent=4, separators=(',',':')))

if __name__ == '__main__':
    main()