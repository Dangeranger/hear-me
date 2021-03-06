# A sample Alexa skill for reading poems (web service example)

from __future__ import print_function
from botocore.vendored import requests
import math
import random
import urllib

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Emily Dickinson Poems. Please ask for a poem by saying, Dickinson Poems read me a poem."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask for Emily Dickinson Poems by saying, Dickinson Poems read me a poem."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using Emily Dickinson Poems."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_launch(launch_request, session):
    # Called when the user launches the skill without an intent
    return get_welcome_response()

def on_intent(intent_request, session):
    # Called when the user specifies an intent for this skill
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetDickinsonPoem":
        return build_response({}, build_speechlet_response(intent['name'], get_dickinson_poem(), None, False))
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def get_dickinson_poem():
    req = requests.get('http://poetrydb.org/author/Emily%20Dickinson/title')
    json_title_result = req.json()
    random_title = int(math.floor(random.random()*(len(json_title_result)-0+1)+0))
    print(json_title_result[random_title])
    encoded_title = urllib.quote(json_title_result[random_title]['title'])



    poem_req = requests.get('http://poetrydb.org/author,title/Emily%20Dickinson;' + encoded_title)
    print(poem_req)
    json_poem_result = poem_req.json()
    speechOutput = "The poem is: " + json_poem_result[0]['title'];

    for i in json_poem_result[0]['lines']:
        speechOutput = speechOutput + " " + i

    return speechOutput

def on_session_ended(session_ended_request, session):
    # Called when the user ends the session.
    print("do nothing")

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])