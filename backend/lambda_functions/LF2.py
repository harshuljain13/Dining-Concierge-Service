import uuid
import datetime
import logging
import boto3
import json
from botocore.exceptions import ClientError
import requests
import decimal
from requests_aws4auth import aws4auth

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(0,len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
        # In my original code I'm converting to int or float, comment the line above if necessary.
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj
    
def get_sqs_data(queue_name):
    try:
        sqs = boto3.client('sqs')
        sqs_queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
        response = sqs.receive_message(
            QueueUrl=sqs_queue_url,
            MessageAttributeNames=[
                'location', 'cuisine', 'time', 'num_people'
            ],
            MaxNumberOfMessages=10,
            VisibilityTimeout=10,
            WaitTimeSeconds=20,
            ReceiveRequestAttemptId=str(uuid.uuid1()).replace("-", "")
            )
        messages = response['Messages'] if 'Messages' in response.keys() else []
        
        for message in messages:
            receiptHandle = message['ReceiptHandle']
            sqs.delete_message(QueueUrl=sqs_queue_url, ReceiptHandle=receiptHandle)
            
        return messages
    except ClientError as e:
        logging.error(e) 
        return []

def compose_es_payload(msg_attributes, n):
    epoch = datetime.datetime.utcfromtimestamp(0)
    seed = (datetime.datetime.utcnow() - epoch).total_seconds() * 1000.0
    return {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"cuisine": msg_attributes['cuisine'].lower()}}
                        ]
                    }
                },
                "random_score": {"seed": str(seed)},
                "score_mode": "sum"
            }
        },
        "from": 0,
        "size": n
    }

def es_search(host, payload):
    credentials = boto3.Session(region_name='us-east-1', aws_access_key_id='AKIATMX4AJ2YCJOVKXXP',
                            aws_secret_access_key='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').get_credentials()
    awsauth = aws4auth.AWS4Auth(credentials.access_key, credentials.secret_key, 'us-east-1', 'es', session_token=credentials.token)
    response = requests.get(host + "/_search", auth=awsauth, json=payload)
    logging.info('response : {}'.format(response))
    return response.json()
    
def get_dynamo_data(dynno, table, key):
    response = table.get_item(Key={'id':key}, TableName='yelp-restaurants')
    
    response = replace_decimals(response)
    name = response['Item']['name']
    address = []
    a_list = response['Item']['address']
    address = ','.join(a_list)
    return '{}, {}'.format(name, address)

def lambda_handler(event, context):
    es_host = 'https://search-dining-concierge-ogeltqbendc4e6kdwwrhhqhjzq.us-east-1.es.amazonaws.com/restaurants'
    table_name = 'yelp-restaurants'
    
    messages = get_sqs_data('Q1')
    
    logging.info(messages)
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    for message in messages:
        logging.info(message)
        msg_attributes = json.loads(message["Body"])
        
        es_payload = compose_es_payload(msg_attributes, 5)
        es_result = es_search(es_host, es_payload)
        hits = es_result['hits']['hits']
        
        suggested_restaurants = []
        for hit in hits:
            id = hit['_source']['restaurantId']
            suggested_restaurant = get_dynamo_data(dynamodb, table, id)
            suggested_restaurants.append(suggested_restaurant)
        print(suggested_restaurants)
        
        text = "Hello! Here are the "+msg_attributes['cuisine']+ " suggestions for "+msg_attributes['num_people']+" people at "+ msg_attributes['time']+" "
        for i,rest in enumerate(suggested_restaurants):
	        text += "(" + str(i+1) + ")" + rest
        
        logging.info(text)
        
        phone_number = msg_attributes['phone_number']
        sns_ = boto3.client('sns')
        sns_.publish(PhoneNumber = phone_number, Message=text, MessageStructure='string')