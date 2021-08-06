from flask import Flask, request, g
import sqlite3
import datetime
import os
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
app = Flask(__name__)

### SQLITE3 DATABASES

DATABASE = 'db.db'
DATABASE_MSG = 'message.db'

HELPMSG = """
*Bandung Help Prompt*
"""

def query_db(query, args=(), one=False, cmt=False):
	conn = get_db()
	cur = conn.execute(query, args)
	if cmt:
		conn.commit()
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv


@app.route("/", methods=['GET', 'POST'])
def index():
	if (request.method == 'GET'):

		app.logger.info("index - GET method")
		return "Hello World Updated!"
	
	elif (request.method == 'POST'):
		app.logger.info("index - POST method")
		app.logger.info("index - request.values = {}".format(str(request.values)))

		incoming_msg = request.values.get('Body', None)

		resp.message("you typed: " + str(incoming_msg))

		return str(resp)

@app.route("/addContact", methods=['POST'])
def addContact():
	if (request.form.get("userFrom") is None or request.form.get("userTo") is None or request.form.get("codeName") is None):
		return "Failed to add contact"
	print("sql statement", flush=True)
	print('INSERT INTO contact (userFrom, userTo, codeName) VALUES("{}", "{}", "{}")'.format(request.form.get("userFrom"), request.form.get("userTo"), request.form.get("codeName")), flush=True)
	x = query_db('INSERT INTO contact (userFrom, userTo, codeName) VALUES("{}", "{}", "{}")'.format(request.form.get("userFrom"), request.form.get("userTo"), request.form.get("codeName")), cmt=True)
	print(x, flush=True)
	return "Successfully added contact"

@app.route("/getContact", methods=['POST'])
def getContact():
	if (request.form.get("userFrom") is None or request.form.get("codeName") is None):
		app.logger.warning("getContact - invalid parameters")
		return "Failed to get contact"
	app.logger.info("getContact - querying from DB")
	x = query_db('SELECT userTo FROM contact WHERE userFrom="{}" AND codeName="{}"'.format(request.form.get("userFrom"), request.form.get("codeName")))
	app.logger.info(x)
	return str(x)

@app.route("/freeze/<name>", methods=['GET'])
def freeze(name):
	### obtain a mapping of numbers to codename for user name
	x = query_db('SELECT * FROM contact WHERE userFrom="{}"'.format(name))
	msg = ""
	for i in x:
		if (msg != ""):
			msg = msg + "\n"
		msg = msg + i[1] + " -> " + i[2]
	return str(msg)
    #return "Hello {}!".format(name)

@app.route("/getAll", methods=['GET'])
def getAll():
	return str(query_db('SELECT * FROM contact'))


if __name__ == "__main__":
	app.run(debug=True)

#https://www.twilio.com/blog/build-a-sms-chatbot-with-python-flask-and-twilio
#https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms?frameUrl=%2Fconsole%2Fsms%2Flogs%3F__override_layout__%3Dembed%26bifrost%3Dtrue%26x-target-region%3Dus1&currentFrameUrl=%2Fconsole%2Fsms%2Flogs%3F__override_layout__%3Dembed%26bifrost%3Dtrue%26x-target-region%3Dus1




