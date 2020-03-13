from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import datetime
from time import sleep
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

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

res = es.search(index="restaurants", doc_type="restaurant", body={"query": {"match": {"cuisine": "indian"}}})

print('searches are: ',res)










