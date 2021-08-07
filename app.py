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

def nicely_format(lis):
	lis.reverse()
	msg = ""
	for i in lis:
		if (msg != ""):
			msg = msg + "\n\n"
		msg = msg + "*[" + i[0] + "]*" + "\n"
		msg = msg + "_" + i[1][9:] + "_ -> _" + i[2][9:] + "_:\n"
		msg = msg + i[3] + "\n"
	return msg

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
	return db

def get_db_msg():
	db = getattr(g, '_database_msg', None)
	if db is None:
		db = g._database_msg = sqlite3.connect(DATABASE_MSG)
	return db

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	db_msg = getattr(g, '_database_msg', None)
	if db is not None:
		db.close()
	if db_msg is not None:
		db_msg.close()

def query_db(query, args=(), one=False, cmt=False):
	conn = get_db()
	cur = conn.execute(query, args)
	if cmt:
		conn.commit()
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

def query_db_msg(query, args=(), one=False, cmt=False):
	conn = get_db_msg()
	cur = conn.execute(query, args)
	if cmt:
		conn.commit()
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

def _getContact(userFrom, codeName):
	x = query_db('SELECT userTo FROM contact WHERE userFrom="{}" AND codeName="{}"'.format(userFrom, codeName))
	return x

def _addContact(userFrom, userTo, codeName):
	x = query_db('INSERT INTO contact (userFrom, userTo, codeName) VALUES("{}", "{}", "{}")'.format(userFrom, userTo, codeName), cmt=True)
	print(x, flush=True)
	return "Successfully added contact"

def _addMessage(userFrom, userTo, message):
	datemsg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	x = query_db_msg('INSERT INTO tb (date, userFrom, userTo, message) VALUES("{}", "{}", "{}", "{}")'.format(datemsg, userFrom, userTo, message), cmt=True)
	print(x, flush=True)
	return "Successfully added message"

def _retrieveLast(userFrom, userTo):
	x = query_db_msg('SELECT * FROM tb WHERE userFrom IN ("{}", "{}") AND userTo IN ("{}", "{}") ORDER BY date DESC LIMIT 3'.format(userFrom, userTo, userFrom, userTo))
	print(x, flush=True)
	return x

@app.route("/", methods=['GET', 'POST'])
def index():
	if (request.method == 'GET'):

		app.logger.info("index - GET method")
		return "Hello World Updated!"
	
	elif (request.method == 'POST'):
		app.logger.info("index - POST method")
		app.logger.info("index - request.values = {}".format(str(request.values)))

		incoming_msg = request.values.get('Body', None)
		sender = request.values.get('From', '')
		recipient = request.values.get('To', '')
		resp = MessagingResponse()

		app.logger.info("index - incoming msg: {}".format(incoming_msg))
		app.logger.info("index - sender is {}".format(sender))

		msg = str(incoming_msg).split()
		if (len(msg) == 0):
			app.logger.warning("index - empty message detected")
			resp.message("Please send an non-empty message. Type $help for guidance.")
			return str(resp)
		
		firstWord = msg[0]
		if (len(firstWord) == 0):
			app.logger.warning("index - first word failed")
			resp.message("Unable to verify command word. Type $help for guidance.")
			return str(resp)
		
		if (firstWord[0] == '$'):
			app.logger.info("index - command word detected")
			lmsg = firstWord[1:]

			if (lmsg == "help"):
				#help
				app.logger.info("index - $help")
				resp.message(HELPMSG)
				return str(resp)
			elif (lmsg == "freeze"):
				#freeze
				app.logger.info("index - $freeze")
				lis = freeze(sender)
				app.logger.info("index - lis = {}".format(str(lis)))
				resp.message(str(lis))
				return str(resp)
			elif (lmsg == "get"):
				#get
				app.logger.info("index - $get")
				if (len(msg) != 2):
					app.logger.warning("index - $get should have two parameters")
					resp.message("Invalid command format. Type $help for guidance.")
					return str(resp)
				respmsg = _getContact(sender, msg[1])
				app.logger.info("index - respmsg = {}".format(str(respmsg)))
				if (len(respmsg) == 0):
					app.logger.warning("index - no contacts obtained")
					resp.message("No such contact exist.")
					return str(resp)
				resp.message(respmsg[0][0])
				return str(resp)
			elif (lmsg == "add"):
				#add
				app.logger.info("index - $add")
				if (len(msg) != 3):
					app.logger.warning("index - $add should have three parameters")
					resp.message("Invalid command format. Type $help for guidance.")
					return str(resp)
				receiver = msg[2]
				if ("+" not in receiver):
					### assume SG
					receiver = "whatsapp:+65" + receiver
				elif ("whatsapp:" not in receiver):
					### assume country code in place
					receiver = "whatsapp:" + receiver
				app.logger.info("index - final receiver = {}".format(str(receiver)))
				_addContact(sender, receiver, msg[1])
				resp.message("Successfully added contact.")
				return str(resp)
			elif (lmsg == "last"):

				app.logger.info("index - $last")
				if (len(msg) != 2):
					app.logger.warning("index - $last should have two parameters")
					resp.message("Invalid command format. Type $help for guidance.")
					return str(resp)
				respmsg = _getContact(sender, msg[1])
				app.logger.info("index - respmsg = {}".format(str(respmsg)))
				if (len(respmsg) == 0):
					app.logger.warning("index - no contacts obtained")
					resp.message("No such contact exist.")
					return str(resp)
				
				x = _retrieveLast(sender, respmsg[0][0])

				resp.message(nicely_format(x))
				return str(resp)

			else:
				app.logger.warning("index - invalid key word")
				resp.message("Invalid command key word. Type $help for guidance.")
				return str(resp)

		elif (firstWord[0] == '@'):
			app.logger.info("index - sending to another person")
			if (len(msg) <= 1 or len(firstWord) <= 1):
				app.logger.warning("index - invalid input message")
				resp.message("Invalid command format. Type $help for guidance.")
				return str(resp)
			msglis = " ".join(msg[1:])
			dirrecipient = _getContact(sender, firstWord[1:])
			app.logger.info("index - dirrecipient = {}".format(str(dirrecipient)))
			#app.logger.info("{}".format(str(dirrecipient)))
			#app.logger.info("{}".format(str(dirrecipient[0])))
			
			if (len(dirrecipient) == 0):
				app.logger.warning("index - unable to find such a recipient")
				resp.message("No such recipient registered. Type $help for guidance.")
				return str(resp)

			resp.message("You are sending to '{}' the following message: {}".format(dirrecipient[0][0], msglis))
			
			### add message to db_msg
			_addMessage(sender, dirrecipient[0][0], msglis)

			### send to the person
			if (firstWord[1:] in ["me", "dad", "mum", "son", "boy", "bro", "brother"]):
				account_sid = os.environ['TWILIO_ACCOUNT_SID']
				auth_token = os.environ['TWILIO_AUTH_TOKEN']
				client = Client(account_sid, auth_token)
				app.logger.info("sender is {}".format(sender))
				app.logger.info("recipient is {}".format(dirrecipient[0][0]))
				app.logger.info("message is {}".format(msglis))

				finmsg = "Message from {}\n\n".format(sender) + msglis

				message = client.messages.create(
					body=finmsg,
					from_="whatsapp:+14155238886",
					to=dirrecipient[0][0]
				)
				app.logger.info("message sent - message.sid = {}".format(message.sid))
			
			return str(resp)
		else:
			
			incoming_msg

			resp.message("Unable to understand message. Type $help for guidance.")
			return str(resp)
		
		resp.message("you typed: " + str(incoming_msg))
		#msg = resp.message()
		#msg.body("you typed: " + str(incoming_msg))
		#print(request.__dict__.items(), flush=True)
		#print(str(request["Body"]), flush=True)
		#print(str(request), flush=True)
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

@app.route("/getLast", methods=['POST'])
def getLast():
	if (request.form.get("userFrom") is None or request.form.get("userTo") is None):
		app.logger.warning("getLast - invalid parameters")
		return "Failed to get last"
	app.logger.info("getLast - querying from DB")
	app.logger.info(request.form.get("userFrom"))
	app.logger.info(request.form.get("userTo"))
	x = _retrieveLast(request.form.get("userFrom"), request.form.get("userTo"))
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

@app.route("/getAllMessage", methods=['GET'])
def getAllMessage():
	return str(query_db_msg('SELECT * FROM tb'))


if __name__ == "__main__":
	app.run(debug=True)

#https://www.twilio.com/blog/build-a-sms-chatbot-with-python-flask-and-twilio
#https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms?frameUrl=%2Fconsole%2Fsms%2Flogs%3F__override_layout__%3Dembed%26bifrost%3Dtrue%26x-target-region%3Dus1&currentFrameUrl=%2Fconsole%2Fsms%2Flogs%3F__override_layout__%3Dembed%26bifrost%3Dtrue%26x-target-region%3Dus1
