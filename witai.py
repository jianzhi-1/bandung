from wit import Wit
import datetime
import logging
import requests
import os
from functools import cmp_to_key

def cmp(a, b):
    if (a['confidence'] == b['confidence']): return 0
    elif (a['confidence'] < b['confidence']): return 1
    else: return -1

class WitBot:
    def __init__(self):
        self.access_token = os.environ['WIT_AI_ACCESS_TOKEN']
        self.client = Wit(self.access_token)
        self.client.logger.info("WitBot initiated")
    
    def query(self, msg):
        resp = self.client.message(msg)
        cmp_key = cmp_to_key(cmp)
        resp['intents'].sort(key=cmp_key)

        self.client.logger.info("WitBot - querying {} response: ".format(msg))
        self.client.logger.info(str(resp['intents']))

        if (len(resp['intents']) == 0):
            return (False, "Unable to understand message. Type $help for guidance.")
        else:
            if (resp['intents'][0]['confidence'] > 0.8):
                return (True, (resp['intents'][0]['name'], resp['intents'][0]['confidence']))
            else:
                if (len(resp['intents']) > 1):
                    return (False, "No recipient indicated.\nDo you mean to send to *@{}* (_{} sure_) or {} ({} sure)?".format(resp['intents'][0]['name'], str(int(100.0*resp['intents'][0]['confidence'])) + "%", resp['intents'][1]['name'], str(int(100.0*resp['intents'][1]['confidence'])) + "%"))
                else:
                    return (False, "No recipient indicated.\nDo you mean to send to *@{}* (_{} sure_)?".format(resp['intents'][0]['name'], str(int(100.0*resp['intents'][0]['confidence'])) + "%"))

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
        self.client.logger.info("WitBot - creating new intent {}".format(intent_name))
        x = requests.post('https://api.wit.ai/intents?v={}'.format(dt), json=data, headers=headers)
        self.client.logger.info("WitBot - SUCCESS")
        return

    
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
        self.client.logger.info("WitBot - training intent {} with text {}".format(intent_name, text))
        x = requests.post('https://api.wit.ai/utterances?v={}'.format(dt), json=data, headers=headers)
        self.client.logger.info("WitBot - SUCCESS")

        return
