from wit import Wit
import logging
import os

access_token = os.environ['WIT_AI_ACCESS_TOKEN']

client = Wit(access_token)
resp = client.message('Hi Boss')
print(type(resp), flush=True)
print('Yay, got Wit.ai response: ' + str(resp), flush=True)

# client.create_intent(intent_name)

# client.train()
