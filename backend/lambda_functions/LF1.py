"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
import json
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def send_sqs_message(QueueName, msg_body):
    """
    :param QueueName: String name of existing SQS queue
    :param msg_body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """

    # Send the SQS message
    sqs_client = boto3.client('sqs')    
    sqs_queue_url = sqs_client.get_queue_url(QueueName=QueueName)['QueueUrl']
    try:
        msg = sqs_client.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(msg_body)) 
    except ClientError as e:
        logging.error(e) 
        return None
    return msg
    
""" --- Functions that control the bot's behavior --- """
def validate_parameters(time_, cuisine, location, num_people, phone_number):
    
    # cuisine validation
    cuisine_types = ['chinese', 'south indian', 'north indian', 'american', 'mexican']
    if not cuisine:
        return build_validation_result(False, 'cuisine', 'What cuisine do you prefer?')
        
    elif cuisine.lower() not in cuisine_types:
        return build_validation_result(False, 'cuisine', 'We do not have any restaurant serving {}, would you like a different cuisine'.format(cuisine))
    
    # time validation
    if not time_:
        return build_validation_result(False, 'time', 'What time do you prefer?')
    
    # location validation
    if not location:
        return build_validation_result(False, 'location', 'Which city do you prefer?')

    # location validation
    if not num_people:
        return build_validation_result(False, 'num_people', 'How many of you are going?')
    
    if not phone_number:
        return build_validation_result(False, 'phone_number', 'Please share your phone number')
    
    
    return build_validation_result(True, None, None)

def get_restaurants(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    
    source = intent_request['invocationSource']
    
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)
        
        time_ = slots["time"]
        cuisine = slots["cuisine"]
        location = slots["location"]
        num_people = slots["num_people"]
        phone_number = slots["phone_number"]
        
        slot_dict = {
            'time': time_,
            'cuisine': cuisine,
            'location': location,
            'num_people': num_people,
            'phone_number': phone_number
        }
        
        validation_result = validate_parameters(time_, cuisine, location, num_people, phone_number)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        #output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        #if flower_type is not None:
        #    output_session_attributes['Price'] = len(flower_type) * 5  # Elegant pricing model

        #return delegate(output_session_attributes, get_slots(intent_request))s
    
    res = send_sqs_message('Q1', slot_dict)
    
    if res:
        response = {
                    "dialogAction":
                        {
                         "fulfillmentState":"Fulfilled",
                         "type":"Close",
                         "message":
                            {
                              "contentType":"PlainText",
                              "content": "Cool! we have received your request. You will soon have a message on your phone with recommendations enlisted! {},{},{},{},{}".format(
                                  time_, cuisine, location, num_people, phone_number),
                            }
                        }
        }
    else:
        response = {
                    "dialogAction":
                        {
                         "fulfillmentState":"Fulfilled",
                         "type":"Close",
                         "message":
                            {
                              "contentType":"PlainText",
                              "content": "We are experiencing problem. Please try after some time!",
                            }
                        }
                    }
    return response

def greet(intent_request):
    session_attributes = intent_request['sessionAttributes']
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitIntent',
            'message': {
                "contentType": "PlainText",
                "content": "Hey Buddy, How can I help you?"
            }
        }
    }
    
    return response


def thankyou(intent_request):
    response = {
        'sessionAttributes': intent_request['sessionAttributes'],
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': 'You are welcome. Good Bye!'
                
            }
        }
    }
    
    return response


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return greet(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thankyou(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return get_restaurants(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
