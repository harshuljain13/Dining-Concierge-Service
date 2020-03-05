from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import datetime
from boto3.dynamodb.conditions import Key, Attr
import boto.dynamodb2
from boto.dynamodb2.table import Table
from time import sleep
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


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


client = boto3.client("es")




# The endpoint of ES
host = "search-dining-concierge-ogeltqbendc4e6kdwwrhhqhjzq.us-east-1.es.amazonaws.com"



service = "es"
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

count = 0

es.index(index="restaurants", doc_type="restaurant", id=restaurantId, body=document)

# Verify that the document was successfully indexed
check = es.get(index="restaurants", doc_type="restaurant", id=restaurantId)
if check["found"]:
    print("Index %s succeeded" % restaurantId)




