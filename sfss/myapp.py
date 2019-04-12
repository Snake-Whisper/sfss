#!/usr/bin/env python3

from flask import Flask, render_template, request, session, escape, url_for, redirect, g, abort, flash, Markup
import random
import pymysql
from flask_redis import FlaskRedis
from flask_socketio import SocketIO, emit
import time
import json
import mail
from validate_email import validate_email
from functools import wraps
import cgitb

cgitb.enable()

app = Flask(__name__)

app.config.update(
	SECRET_KEY = '\x81H\xb8\xa3S\xf8\x8b\xbd"o\xca\xd7\x08\xa4op\x07\xb5\xde\x87\xb8\xcc\xe8\x86\\\xffS\xea8\x86"\x97',
	REDIS_URL = "redis://localhost:6379/0",
	AUTO_LOGOUT = 43200
)
socketio = SocketIO(app)
#socketio = SocketIO(app, message_queue="redis://")

@socketio.on('my event')
def handle_my_custom_event(json):
	print('received json: ' + str(json['data']))
	emit("response", json['data'], broadcast=True)


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

def chkLogin(username, password):
	cursor = getDBCursor()
	res = cursor.execute("SELECT id FROM users WHERE (username = %s or email = %s) AND password=PASSWORD(%s)", (username, username, password))#TODO test!)
	cursor.close()
	return res > 0#TODO Decide if == 1 better? Norm no diff

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
		#return render_template("register.html", email=request.form["email"])
		return render_template("message.html", message="Successful send email with registration key to <strong>{0}</strong>. Please check your <strong>SPAM-Folder</strong> too. <br />Back to <a href='{1}'>login</a>".format(Markup(request.form["email"]), url_for('login')))
	else:
		return render_template("register.html")

def __addChatEntry(DBdescriptor, author, chatID, content, file=""):
	if file:
		DBdescriptor.execute("INSERT INTO chatEntries (author, ChatID, file, content) VALUES (%s, %s, %s, %s)", (author, chatID, file, content))
	else:
		DBdescriptor.execute("INSERT INTO chatEntries (author, ChatID, content) VALUES (%s, %s, %s)", (author, chatID, content))

def _addChatEntry(author, chatID, content, file=""):
	__addChatEntrie(getDBCursor(),  author, chatID, content, file)
	
def __addChat(DBdescriptor, name, UID, GID, OwnerPermission=7, GroupPermission=6, OtherPermission=0, admins=""):
	DBdescriptor.execute("INSERT INTO chats (name, UID, GID, OwnerPermission, GroupPermission, OtherPermission, admins) VALUES (%s, %s, %s, %s, %s, %s, %s)", (name, UID, GID, OwnerPermission, GroupPermission, OtherPermission, admins))

def _addChat(name, UID, GID, OwnerPermission=7, GroupPermission=6, OtherPermission=0, admins=""):
	__addChat(getDBCursor(), name, UID, GID, OwnerPermission, GroupPermission, OtherPermission, admins)

def _addGroup(groupname, owner, members="", admins=""):
	__addGroup(groupname, owner, members, admins)

def __addGroup(DBdescriptor, groupname, owner, members='', admins=""):
	DBdescriptor.execute("INSERT INTO groups (groupname, owner, members, admins) VALUES (%s, %s, %s, %s)", (groupname, owner, members, admins))

def _addFile(chatID, owner, url, fileNO="NULL",  position=0):
	__addFile(getDBCursor(), fileNO, lastAuthor, chatID, position, owner, url)

def __addFile(DBdescriptor, chatID, owner, url, fileNO="",  position=0):
	if fileNO:
		DBdescriptor.execute("INSERT INTO files (fileNO, chatID, position, owner, url) VALUES (%s, %s, %s, %s, %s)", (fileNO, chatID, position, owner, url))
	else:
		DBdescriptor.execute("INSERT INTO files (chatID, position, owner, url) VALUES (%s, %s, %s, %s)", (chatID, position, owner, url))

########################################## getter ###############################################

def query(query, param = ()):
	cursor = getDBCursor()
	cursor.execute(query, param)
	return cursor.fetchall()

def _getUser(user):
	cursor = getDBCursor()
	cursor.execute("SELECT id from users where username = %s or email = %s", (user, user,))
	return cursor.fetchall()[0]["id"]

def getOwnUser():
	return _getUser(session["username"])

def _getChats(userID):
	return query("SELECT name FROM chats WHERE UID = %s", (userID,))

def getOwnChats():
	return _getChats(session["userID"])

def getChatEntries(chatID):
	#return query("select author, ctime, file, content from chatEntries where ChatID = %s", (chatID,))
	return query("SELECT users.username, chatEntries.ctime, chatEntries.file, chatEntries.content FROM chatEntries INNER JOIN users ON chatEntries.author=users.id WHERE chatEntries.ChatID = %s", (chatID,))


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
	

@app.route("/listChats")
@login_required
def listChats():
	return render_template("listChats.html", entries=getOwnChats())

@app.route("/listChatEntries/<id>")
@login_required
def listChatEntries(id):
	return render_template("listChatEntries.html", entries=getChatEntries(id))

@app.route("/")
@login_required
def home():
	return render_template("workspace.html")
@app.route("/notImpl/<item>")
@login_required
def notImpl(item):
	return "The requestet site or service {0} hasn't been implemented yet. So it's time to do it. You know?".format(item)

@app.route("/login/", methods=["POST", "GET"])
def login():
	if 'username' in session and "authID" in session:
		return redirect('/')
	if request.method == 'POST':
		if all([request.form['username'], request.form['password']]) and chkLogin(request.form['username'], request.form['password']):
			session['username'] = request.form["username"]
			userid = getOwnUser()
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

@app.cli.command("randomFill")
def randomFill():
	import os #dirty
	os.popen('mysql -u sfss -h 192.168.178.39 -pQsbPu7N0kJ4ijyEf -e "DROP DATABASE sfss; CREATE DATABASE sfss;"')
	time.sleep(2)
	c = getDBCursor()
	with app.open_resource('schema.sql', mode='r') as f:		
		for query in f.read().split(";")[:-1]:
			print(query)
			c.execute(query)
		f.close() 
	_registerUser("b", "b", email="verf@web-utils.ml")
	for i in range(20):
		_registerUser("test"+str(i), "geheim", email="test{0}@web-utils.ml".format(i))
		__addGroup(c, "TestGruppe"+str(i), owner=i, members='test1,test2,test3', admins="test1,test3")
		__addChat(c, "Chat"+str(i), 1, 1, OwnerPermission=7, GroupPermission=6, OtherPermission=0, admins="")
	
	__addFile(getDBCursor(), 1, 1, "/dev/null", position=0)
	c.close()
	g.db.commit() #manual tear down!
	c = getDBCursor()
	for i in range(20):
		for y in range(20):
			__addChatEntry(c, random.randint(1,19), random.randint(1,19), "test"+str(y)) #DBdescriptor, author, chatID, content, file="NULL"
	c.close()
	g.db.commit()

if __name__ == "__main__":
	socketio.run(app)
#	app.run(host='0.0.0.0')
