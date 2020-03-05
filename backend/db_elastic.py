from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import datetime
from boto3.dynamodb.conditions import Key, Attr
import boto.dynamodb2
from boto.dynamodb2.table import Table
from time import sleep

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id='AKIATMX4AJ2YKGC2Z4MT',
         aws_secret_access_key= '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')

Elastic = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id='AKIATMX4AJ2YKGC2Z4MT',
         aws_secret_access_key= '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')
table = dynamodb.Table('yelp-restaurants')


#fe = Key('name')

x    = table.scan()
data = x["Items"]
name=[]
final_data=[]
cuisine =[]
for each_entry in data:
    name.append(each_entry["name"])
    cuisine.append(each_entry["zipcode"]) 
    final_data.append([each_entry["name"],each_entry["zipcode"]])

print (cuisine)




