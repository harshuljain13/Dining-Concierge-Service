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

table = dynamodb.Table('yelp-restaurants')

# The endpoint of ES
host = "search-dining-concierge-ogeltqbendc4e6kdwwrhhqhjzq.us-east-1.es.amazonaws.com"
# Make connection to ES
service = "es"
#awsauth = AWS4Auth([''], [''], region=['us-east-1'], service=service)
credentials = boto3.Session(region_name='us-east-1', aws_access_key_id='AKIATMX4AJ2YCJOVKXXP',
                            aws_secret_access_key='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').get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, 'us-east-1', service)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


x = table.scan()
data = x["Items"]
id=[]
final_data=[]
cuisine =[]
count =0
for each_entry in data:
    id.append(each_entry["id"])
    cuisine.append(each_entry["cuisine"]) 
    document = {
        "restaurantId": each_entry["id"],
        "cuisine": each_entry["cuisine"]
    }
    es.index(index="restaurants", doc_type="restaurant", id=each_entry["id"], body=document)

    count+=1
    # Verify that the document was successfully indexed
    check = es.get(index="restaurants", doc_type="restaurant", id=each_entry["id"])
    if check["found"]:
        print("Index %s succeeded" % each_entry["id"])
        print(count)










