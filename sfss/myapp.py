#!/usr/bin/env python3

from flask import Flask, render_template, request, session, escape, url_for, redirect, g, abort, flash, Markup
import random
import pymysql
from flask_redis import FlaskRedis
import flask_socketio
from flask_socketio import SocketIO, Namespace, emit, join_room, leave_room, rooms
import time
import json
import mail
from werkzeug.utils import secure_filename
import os.path
from validate_email import validate_email
from functools import wraps
import cgitb
import os

cgitb.enable()

app = Flask(__name__)
app.config.update(
	SECRET_KEY = '\x81H\xb8\xa3S\xf8\x8b\xbd"o\xca\xd7\x08\xa4op\x07\xb5\xde\x87\xb8\xcc\xe8\x86\\\xffS\xea8\x86"\x97',
	REDIS_URL = "redis://localhost:6379/0",
	AUTO_LOGOUT = 43200,
	MAX_CONTENT_LENGTH = 30 * 1024 * 1024,
	#DATADIR = "/server/python/pythonapps/sfss/sfss/data"
	DATADIR = "/tmp"
)
socketio = SocketIO(app)
chatdir = os.path.join(app.config["DATADIR"], "files")

############## socket section #################################

class chatNameSpace(Namespace):
	def on_connect(self):
		for i in [i["id"] for i in getOwnChats()]:
			join_room(i)
		emit("setupMe", session["username"])
		emit("loadChatList", json.dumps(getOwnChats()))
		emit("chkWritePerm", {"writePerm" : False}) #change?
		emit("chkUploadPerm", {"uploadPerm" : False})
		emit("chkGrantPerm", {"grantPerm" : False})

	def on_disconnect(self):
		pass
	
	def on_sendPost(self, msg):
		#TODO: check for authority and available!
		if not chkChatWritePerm(msg['chatId']):
			self.bot_answer("You are not alowed to post here!", msg)
			return
		packet = [{"ctime" : time.strftime("%d.%b.%y, %H:%M"), 
				   "username" : session["username"],
				   "content" : msg["content"],
				   "chatId" : msg["chatId"]
				  }]
		_addChatEntry(session["userID"], msg["chatId"], msg["content"])
		emit("recvPost", json.dumps(packet), room=int(msg["chatId"])) #disable broadcast!!!
		
	def on_cdChat(self, msg):
		if not chkChatReadPerm(msg['chatId']):
			self.bot_answer("This chat isn't visible to you (anymore)", msg)
			emit("loadChatList", json.dumps(getOwnChats()))
			return
		chatEntries = getChatEntries(msg["chatId"])
		for i in range(len(chatEntries)):
			chatEntries[i]["ctime"] = format_datetime(chatEntries[i]["ctime"])
		emit("loadChat", json.dumps(chatEntries))
		emit("chkWritePerm", {"writePerm" : chkChatWritePerm(msg["chatId"])})
		emit("chkUploadPerm", {"uploadPerm" : chkChatUploadPerm(msg["chatId"])})
		emit("chkGrantPerm", {"grantPerm" : chkChatGrantPerm(msg["chatId"])})
		
	
	def on_chkWritePerm(self, msg):
		emit("chkWritePerm", {"writePerm" : chkChatWritePerm(msg["chatId"])})
	def on_chkUploadPerm(self, msg):
		emit("chkUploadPerm", {"uploadPerm" : chkChatUploadPerm(msg["chatId"])})
	def on_chkGrantPerm(self, msg):
		emit("chkGrantPerm", {"grantPerm" : chkChatGrantPerm(msg["chatId"])})
	
	
	
	def bot_answer(self, answer, msg):
		self.packet = [{"ctime" : time.strftime("%d.%b.%y, %H:%M"), 
				   "username" : "BOT",
				   "content" : answer,
				   "chatId" : msg["chatId"]
				  }]
		
		emit("recvPost", json.dumps(self.packet))
		
socketio.on_namespace(chatNameSpace("/chat"))
		
##############################################################

@app.route("/settings")
def settings():
	return redirect("/notImpl/settings")

def chkID():
	if not 'authID' in session or not "userID" in session:
		logout()
		return False
	key = getRedis().get(session['authID'])
	if not key or key.decode() != session["userID"]:
		logout()
		return False
	return True

def login_required(f):
	@wraps(f)
	def dec_funct(*args, **kwargs):
		if not 'username' in session or not chkID():
			return redirect("/login")
		return f(*args, **kwargs)
	return dec_funct

def getRedis():
	if not hasattr(g, 'redis'):
		g.redis = FlaskRedis(app)
	return g.redis
	
def getDBCursor():
	if not hasattr(g, 'db'):
		g.db = pymysql.connect(user='sfss', password='QsbPu7N0kJ4ijyEf', db='sfss', cursorclass=pymysql.cursors.DictCursor, host="192.168.178.39")
		#g.db = pymysql.connect(user='sfss', password='QsbPu7N0kJ4ijyEf', db='sfss', cursorclass=pymysql.cursors.DictCursor, host="localhost")
	return g.db.cursor()

@app.teardown_appcontext
def closeDB(error):
	if hasattr(g, 'db'):
		g.db.commit()
		g.db.close()
		
##################### DB section ##############################################################

def _registerUser(username, password, firstName="null", lastName="null", email="null", enabled=1):
	cursor = getDBCursor()
	cursor.execute("INSERT INTO users (username, password, firstName, lastName, email, enabled) VALUES (%s, PASSWORD(%s), %s, %s, %s, %s)", (username, password, firstName, lastName, email, enabled)) #TODO test!
	cursor.close()

@app.route("/register/", methods=['POST', 'GET'])
def register():
	if request.method == 'POST':
		if not all([request.form["username"] , request.form["password"], request.form["Confpassword"], request.form["firstName"], request.form["lastName"], request.form["email"]]):
			flash("Please fill all fields")
			return redirect("/register")
		if request.form["password"] != request.form["Confpassword"]:
			flash("Please check your password")
			return redirect("/register")
		if not validate_email(request.form["email"]):
			flash("Please check your email address")
			return redirect("/register")
		
		cursor = getDBCursor()	
		if cursor.execute("SELECT id FROM users WHERE username = %s", (request.form["username"])) > 0:
			flash("User allready Exists")
			cursor.close()
			return redirect("/register")
		if cursor.execute("SELECT id FROM users WHERE email = %s", (request.form["email"])) > 0:
			flash("Email allready taken")
			cursor.close()
			return redirect("/register")
		key = mail.sendRegisterKey(request.form["email"])
		r = getRedis()
		r.set(key, json.dumps({"username": request.form["username"],
								"password": request.form["password"],
								"firstName":request.form["firstName"],
								"lastName": request.form["lastName"],
								"email"		: request.form["email"]}), 600)
		return render_template("message.html", message="Successful send email with registration key to <strong>{0}</strong>. Please check your <strong>SPAM-Folder</strong> too. <br />Back to <a href='{1}'>login</a>".format(Markup(request.form["email"]), url_for('login')))
	else:
		return render_template("register.html")

####################################### checker #####################################################################

def chkLogin(username, password):
	cursor = getDBCursor()
	res = cursor.execute("SELECT id FROM users WHERE (username = %s or email = %s) AND password=PASSWORD(%s)", (username, username, password))#TODO test!)
	cursor.close()
	return res > 0#TODO Decide if == 1 better? Norm no diff

	

def chkChatReadPerm(chatID):
	try:
		chatID = int(chatID)
		return chatID == query("SELECT id FROM chats WHERE chats.id = %s and (chats.UID=%s OR FIND_IN_SET(%s, chats.readUsers) OR SET_IN_SET((SELECT groups from users where id=%s), chats.readGroups))", (chatID, session["userID"], session["userID"], session["userID"], ))[0]['id']
	except:
		return False
	
def chkChatWritePerm(chatID):
	try:
		chatID = int(chatID)
		return chatID == query("SELECT id FROM chats WHERE chats.id = %s and (chats.UID=%s OR FIND_IN_SET(%s, chats.writeUsers) OR SET_IN_SET((SELECT groups from users where id=%s), chats.writeGroups))", (chatID, session["userID"], session["userID"], session["userID"], ))[0]['id']
	except:
		return False

def chkChatGrantPerm(chatID):
	try:
		chatID = int(chatID)
		return chatID == query("SELECT id FROM chats WHERE chats.id = %s and (chats.UID=%s OR FIND_IN_SET(%s, chats.grantUsers) OR SET_IN_SET((SELECT groups from users where id=%s), chats.grantGroups))", (chatID, session["userID"], session["userID"], session["userID"], ))[0]['id']
	except:
		return False

def chkChatUploadPerm(chatID):
	try:
		chatID = int(chatID)
		return chatID == query("SELECT id FROM chats WHERE chats.id = %s and (chats.UID=%s OR FIND_IN_SET(%s, chats.uploadUsers) OR SET_IN_SET((SELECT groups from users where id=%s), chats.uploadGroups))", (chatID, session["userID"], session["userID"], session["userID"], ))[0]['id']
	except:
		return False


############################################### adder ###############################################################

def __addChatEntry(DBdescriptor, author, chatID, content, file="", ctime=None):
	if not ctime:
		ctime = time.strftime("%Y-%m-%d %H:%M:%S")
	if file:
		DBdescriptor.execute("INSERT INTO chatEntries (author, ChatID, file, content, ctime) VALUES (%s, %s, %s, %s, %s)", (author, chatID, file, content, ctime))
	else:
		DBdescriptor.execute("INSERT INTO chatEntries (author, ChatID, content, ctime) VALUES (%s, %s, %s, %s)", (author, chatID, content, ctime))

def _addChatEntry(author, chatID, content, file="", time=None):
	__addChatEntry(getDBCursor(),  author, chatID, content, file, time)
	
def __addChat(DBdescriptor, name, UID, readUsers="", readGroups="", writeUsers="", writeGroups="", uploadUsers="", uploadGroups="", grantUsers="", grantGroups="", OtherPermission=""):
	DBdescriptor.execute("INSERT INTO chats (name, UID, readUsers, readGroups, writeUsers, writeGroups, uploadUsers, uploadGroups, grantUsers, grantGroups, OtherPermission) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, UID, readUsers, readGroups, writeUsers, writeGroups, uploadUsers, uploadGroups, grantUsers, grantGroups, OtherPermission))

def _addChat(name, UID, readUsers="", readGroups="", writeUsers="", writeGroups="", uploadUsers="", uploadGroups="", grantUsers="", grantGroups="", OtherPermission=""):
	__addChat(getDBCursor(), name, UID, GID, OwnerPermission, GroupPermission, OtherPermission, admins)

def _addGroup(groupname, owner, members="", admins=""):
	__addGroup(groupname, owner, members, admins)

def __addGroup(DBdescriptor, groupname, owner, members='', admins=""):
	DBdescriptor.execute("INSERT INTO groups (groupname, owner, members, admins) VALUES (%s, %s, %s, %s)", (groupname, owner, members, admins))

def _addFile(chatID, owner, url):
	__addFile(getDBCursor(), chatID, owner, url)

def __addFile(DBdescriptor, chatID, owner, url):
	DBdescriptor.execute("INSERT INTO files (chatID, owner, url) VALUES (%s, %s, %s)", (chatID, owner, url))

def _addFileVersion(chatID, fileNO, owner, url):
	__addFile(getDBCursor(), chatID, fileNO, owner, url)

def __addFileVersion(DBdescriptor, chatID, fileNO, owner, url):
	DBdescriptor.execute("INSERT INTO files (chatID, fileNO, owner, url) VALUES (%s, %s, %s, %s)", (chatID, fileNO, owner, url))

########################################## getter ###############################################

def query(query, param = ()):
	cursor = getDBCursor()
	cursor.execute(query, param)
	return cursor.fetchall()

def _getUser(user):
	cursor = getDBCursor()
	cursor.execute("SELECT id from users where username = %s or email = %s", (user, user,))
	return cursor.fetchall()[0]["id"]

def getOwnUserID():
	return _getUser(session["username"])

def getUsername(username):
	return query("SELECT username FROM users WHERE username = %s OR email = %s", (username, username,))[0]["username"]

def _getChats(userID):
	return query("SELECT chats.name, chats.id FROM chats WHERE chats.UID = %s OR FIND_IN_SET(%s, chats.readUsers) OR SET_IN_SET((SELECT groups from users where id = %s), chats.readGroups)", (userID, userID, userID,))

def getOwnChats():
	return _getChats(session["userID"])

def getChatEntries(chatID):
	return query("SELECT users.username, chatEntries.ctime, chatEntries.file, chatEntries.content FROM chatEntries INNER JOIN users ON chatEntries.author=users.id WHERE chatEntries.ChatID = %s", (chatID,))

def getGroups():
	return query("SELECT groups FROM users where id = %s", (session["userID"]))[0]['groups'].split(",")

def _getFiles(id):
	return query("SELECT version, fileNO FROM files WHERE ChatID = %s",(id,)) #TODO: Complete!!!


################################ filter ##########################################################

@app.template_filter('formatdatetime')
def format_datetime(value, format="%d.%b.%y, %H:%M"):
    """Format a date time"""
    if value is None:
        return ""
    return value.strftime(format)

##################################################################################################

@app.route("/registerkey/<key>")
def registerKey(key):
	r = getRedis()
	res = r.get(key)
	if res:
		res = json.loads(res.decode())
		_registerUser(res["username"], res["password"], res["firstName"], res["lastName"], res["email"])
		r.delete(key)
		return render_template("message.html", message="Registration Succesful. Redirection in 3 seconds", refresh=3, redirect=url_for("login"))
	else:
		return render_template("message.html", message="This Key doesn't exist. Remeber, you've only 10 Minutes to continue your registration")
	

@app.route("/")
@login_required
def home():
	return render_template("workspace.html", chats=getOwnChats(), chatEntries=getChatEntries(1))
@app.route("/notImpl/<item>")
@login_required
def notImpl(item):
	return "The requestet site or service {0} hasn't been implemented yet. So it's time to do it. You know?".format(item)

@app.route("/upload", methods=["POST"])
@login_required
def upload():
	global chatdir
	if not all([request.form["chatId"], chkChatUploadPerm(request.form["chatId"])]):
		return abort(401)
	if not "file" in request.files: #ToDO: Improve
		print("abort file transfer")
		return abort(400)
	file = request.files['file']
	filename = "{0}_{1}".format(secure_filename(file.filename), int(time.time()*1000))
	url = os.path.join(chatdir, filename)
	file.save(url)
	_addFile(request.form["chatId"], session["userID"], url)
	print("saved:" + filename)
	return "ok"

@app.route("/login/", methods=["POST", "GET"])
def login():
	if 'username' in session and "authID" in session:
		return redirect('/')
	if request.method == 'POST':
		if all([request.form['username'], request.form['password']]) and chkLogin(request.form['username'], request.form['password']):
			session['username'] = getUsername(request.form['username'])
			userid = getOwnUserID()
			session['userID'] = str(userid)
			key = mail.genKey()
			getRedis().set(key, userid, app.config["AUTO_LOGOUT"])
			session["authID"] = key
			return redirect("/")
		flash("authentication failure")
		return redirect("/login")#replace with correct call of render template?
	return render_template("login.html")

@app.route("/logout")
def logout():
	if 'username' in session or 'authID' in session:
		session.pop('username', None)
		session.pop('userID', None)
		session.pop('ownGroups', None)
		
		getRedis().delete(session.pop('authID', ""))
		return redirect("/login")
	else:
		return redirect("/login")


@app.cli.command('initdb')
def initdb():
	with app.open_resource('schema.sql', mode='r') as f:
		c = getDBCursor()
		for query in f.read().split(";")[:-1]:
			print(query)
			c.execute(query)
		f.close() 
		c.close()
		g.db.commit() #manual tear down!

@app.cli.command("randomFill") #changed auto time!!!
def randomFill():
	import os #dirty
	#os.popen('mysql -u sfss -h localhost -pQsbPu7N0kJ4ijyEf -e "DROP DATABASE sfss; CREATE DATABASE sfss;"')
	os.popen('mysql -u sfss -h 192.168.178.39 -pQsbPu7N0kJ4ijyEf -e "DROP DATABASE sfss; CREATE DATABASE sfss;"')
	time.sleep(2)
	c = getDBCursor()
	with app.open_resource('schema.sql', mode='r') as f:		
		for query in f.read().split(";")[:-1]:
			print(query)
			c.execute(query)
		f.close()
	print("========== Trigger ==========")
	with app.open_resource('trigger.sql', mode='r') as f:		
		for query in f.read().split("$$")[:-1]:
			print(query)
			c.execute(query)
		f.close()

	_registerUser("b", "b", email="verf@web-utils.ml")
	for i in range(20):
		_registerUser("test"+str(i), "geheim", email="test{0}@web-utils.ml".format(i))
		__addGroup(c, "TestGruppe"+str(i), owner=i, members='1,3,4,5', admins="3,4")
		__addChat(c, "Chat"+str(i), 1, readUsers="1,3,5", readGroups="2,4", writeUsers="9,10", writeGroups="4,7", uploadUsers="3,8", uploadGroups="1,2", grantUsers="5,3", grantGroups="1,2", OtherPermission="5")
	
	__addFile(getDBCursor(), 2, 1, "/dev/null")
	__addFileVersion(getDBCursor(), 2, 1, 1, "/dev/null")
	c.close()
	g.db.commit() #manual tear down!
	c = getDBCursor()
	for i in range(20):
		for y in range(20):
			__addChatEntry(c, random.randint(1,19), random.randint(1,19), "test"+str(y)) #DBdescriptor, author, chatID, content, file="NULL"
	c.execute("TRUNCATE TABLE TriggerLog")
	c.close()
	g.db.commit()

if __name__ == "__main__":
	socketio.run(app)
#	app.run(host='0.0.0.0')
