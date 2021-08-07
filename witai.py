from wit import Wit
import datetime
import logging
import requests
import os
from functools import cmp_to_key

#access_token = os.environ['WIT_AI_ACCESS_TOKEN']

def cmp(a, b):
    if (a['confidence'] == b['confidence']): return 0
    elif (a['confidence'] < b['confidence']): return 1
    else: return -1

class WitBot:
    def __init__(self):
        self.access_token = os.environ['WIT_AI_ACCESS_TOKEN']
        self.client = Wit(self.access_token)
    
    def query(self, msg):
        resp = self.client.message(msg)
        cmp_key = cmp_to_key(cmp)
        resp['intents'].sort(key=cmp_key)

        if (len(resp['intents']) == 0):
            return (False, "Sorry. No good suggestions")
        else:
            if (resp['intents'][0]['confidence'] > 0.7):
                return (True, (resp['intents'][0]['name'], resp['intents'][0]['confidence']))
            else:
                if (len(resp['intents']) > 1):
                    return (False, "No recipient indicated. Do you mean to send to {} ({} sure) or {} ({} sure)?".format(resp['intents'][0]['name'], str(int(100.0*resp['intents'][0]['confidence'])) + "%", resp['intents'][1]['name'], str(int(100.0*resp['intents'][1]['confidence'])) + "%"))
                else:
                    return (False, "No recipient indicated. Do you mean to send to {} ({} sure)?".format(resp['intents'][0]['name'], str(int(100.0*resp['intents'][0]['confidence'])) + "%"))
        return resp['intents']

    def _query(self, msg):
        resp = self.client.message(msg)
        cmp_key = cmp_to_key(cmp)
        resp['intents'].sort(key=cmp_key)
        return resp['intents']

    def create_new_intent(self, intent_name):
        headers = {
            "Authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json"
        }
        data = {
            "name": intent_name
        }
        dt = datetime.datetime.now().strftime("%Y%m%d")
        x = requests.post('https://api.wit.ai/intents?v={}'.format(dt), json=data, headers=headers)
        print(x, flush=True)
        return

        #Definition
        #POST https://api.wit.ai/intents
        #Example request
        #$ curl -XPOST 'https://api.wit.ai/intents?v=20200513' \
        #-H "Authorization: Bearer $TOKEN" \
        #-H "Content-Type: application/json" \
        #-d '{"name": "buy_flowers"}'
        #Example response
        #{
        #"id": "13989798788",
        #"name": "buy_flowers"
        #}

    
    def train_intent(self, intent_name, text):

        ### maybe do a check to see if intent name is within the list of intents?

        headers = {
            "Authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json"
        }
        data = [{
            "text": text,
            "intent": intent_name,
            "entities": [],
            "traits": []
        }]
        dt = datetime.datetime.now().strftime("%Y%m%d")
        x = requests.post('https://api.wit.ai/utterances?v={}'.format(dt), json=data, headers=headers)
        print(x)
        #Definition
        #POST https://api.wit.ai/utterances
        #Example request
        #$ curl -XPOST 'https://api.wit.ai/utterances?v=20200513' \
        #-d '[{
        #        "text": "I want to fly to sfo",
        #        "intent": "flight_request",
        #        "entities": [
        #        {
        #            "entity": "wit$location:to",
        #            "start": 17,
        #            "end": 20,
        #            "body": "sfo",
        #            "entities": []
        #        }
        #        ],
        #        "traits": []
        #    }]'
        #Example response
        #{
        #"sent": true,
        #"n": 1
        #}


        return

wb = WitBot()
#print(wb.query("Hi Boss"))
#wb.create_new_intent("plumber")
wb.train_intent("plumber", "Water is overflowing everywhere, help!")

#client = Wit(access_token)
#resp = client.message('Hi Boss')
#print(type(resp), flush=True)
#print('Yay, got Wit.ai response: ' + str(resp), flush=True)

# client.create_intent(intent_name)

# client.train()