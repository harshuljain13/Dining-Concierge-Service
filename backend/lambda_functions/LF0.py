import json
import datetime

def lambda_handler(event, context):
    # TODO implement
    response = {
        'messages': [
            {
                "type":"string",
                "unstructured": {
                    "id":"1",
                    "text": "I’m still under development. Please come back later.",
                    "timestamp": str(datetime.datetime.now().timestamp())
                }
            }
            ]
    }
    
    return response
