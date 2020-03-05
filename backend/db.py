#
#  Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#  This file is licensed under the Apache License, Version 2.0 (the "License").
#  You may not use this file except in compliance with the License. A copy of
#  the License is located at
# 
#  http://aws.amazon.com/apache2.0/
# 
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#  CONDITIONS OF ANY KIND, either express or implied. See the License for the
#  specific language governing permissions and limitations under the License.
#
from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id='AKIATMX4AJ2YKGC2Z4MT',
         aws_secret_access_key= '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')
table = dynamodb.Table('yelp-restaurants')

with open("../data/restaurants_american.json") as json_file:
    restaurants = json.load(json_file)
    count= 0
    for restaurant in restaurants:
        try:
            item = {
            'insertedAtTimestamp': str(datetime.datetime.now().timestamp()*1000),
            'id': restaurant['id'],
            'name': restaurant['name'],
            'rating':str(restaurant['rating']),
            'num_reviews': str(restaurant['review_count']),
            'address' : restaurant['location']['display_address'],
            'coordinates': str(restaurant['coordinates']),
            'zipcode': restaurant['location']['zip_code'],
            'cuisine': 'american'

            }

            table.put_item(Item=item)
            count+=1
        except:
            pass
    print('Number of restaurants inserted: ', count)
