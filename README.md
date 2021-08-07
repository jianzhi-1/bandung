# Bandung

![Bandung Logo](./bandung.png)

Too many contacts in your Whatsapp? Tired of seeing one-time contacts keep popping up? Bandung helps to bundle up these contacts into one Whatsapp chat. What's more? You can give each of these contacts a codename to easily refer to them when whatsapping them!

Bandung is submitted to RoboHacks 2021 (organised by MLH). It is also the last hackathon for two of the team members before they start their university education.

[Bandung Devpost]()
[Bandung Video Demo]()

### Features

1. Bundling up of one-time/temporary/bot contacts!
Everyone has these type of contacts, be it the local pizza shop, the dentist, your personal doctor, the plumber, or even a duty officer that you have to report to everyday.

2. Facilitates easy reference by codifying name
You don't have to remember the people's numbers, or even need to save them to your contact list. Just ```$add <codename> <contact_number>``` (e.g. ```$add pizza 65656565```). The next time you have to whatsapp the pizza store for pizza, just refer to them using ```@pizza```. 

Example: ```@pizza can i have a large hawaiian pizza with 2 garlic bread?```

3. Never lose your contacts

4. Retrieve last send messages 

### Setting Up

1. Setting up environmental variables and DB

```dosini
export TWILIO_ACCOUNT_SID='<TWILIO_ACCOUNT_SID>'
export TWILIO_AUTH_TOKEN='<TWILIO_AUTH_TOKEN>'
export WIT_AI_ACCESS_TOKEN='<WIT_AI_ACCESS_TOKEN'
```

```shell
$ sh setup.sh
```

1. Running Flask app
```shell
$ python3 app.py
```

2. Running ngrok (for mapping of ports)
```shell
$ cd /path/to/ngrok
$ ./ngrok http 5000
```

3. Update Twilio address
Twilio Sandbox
Copy the url generated by ngrok and paste it in Twilio sandbox

4. Done!