#!/usr/bin/env python3

from flask import Flask, render_template, request, session, escape, url_for, redirect, g, abort, flash, Markup
import random
import pymysql
from flask_redis import FlaskRedis
import time
import json
import mail
from validate_email import validate_email
from functools import wraps

app = Flask(__name__)

app.config.update(
	SECRET_KEY = '\x81H\xb8\xa3S\xf8\x8b\xbd"o\xca\xd7\x08\xa4op\x07\xb5\xde\x87\xb8\xcc\xe8\x86\\\xffS\xea8\x86"\x97',
	REDIS_URL = "redis://localhost:6379/0"
)

def login_required(f):
	@wraps(f)
	def dec_funct(*args, **kwargs):
		if not 'username' in session:
			return redirect("/login")
		return f(*args, **kwargs)
	return dec_funct

def getRedis():
	if not hasattr(g, 'redis'):
		g.redis = FlaskRedis(app)
	return g.redis
	
def getDBCursor():
	if not hasattr(g, 'db'):
		g.db = pymysql.connect(user='sfss', password='QsbPu7N0kJ4ijyEf', db='sfss', cursorclass=pymysql.cursors.DictCursor)
	return g.db.cursor()

@app.teardown_appcontext
def closeDB(error):
	if hasattr(g, 'db'):
		g.db.commit()
		g.db.close()

def _registerUser(username, password, firstName="null", lastName="null", email="null", enabled=1):
	cursor = getDBCursor()
	cursor.execute("INSERT INTO users (username, password, firstName, lastName, email, enabled) VALUES (%s, PASSWORD(%s), %s, %s, %s, %s)", (username, password, firstName, lastName, email, enabled)) #TODO test!
	cursor.close()

def chkLogin(username, password):
	cursor = getDBCursor()
	res = cursor.execute("SELECT id FROM users WHERE (username = %s or email = %s) AND password=PASSWORD(%s)", (username, username, password))#TODO test!)
	cursor.close()
	return res > 0#TODO Decide if == 1 better? Norm no diff
	
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

@app.route("/")
def home():
	return render_template("layout.html")
@app.route("/notImpl/<item>")
@login_required
def notImpl(item):
	return "The requestet site or service {0} hasn't been implemented yet".format(item)

@app.route("/login/", methods=["POST", "GET"])
def login():
	if 'username' in session:
		return redirect('/notImpl/loggedIn')
	if request.method == 'POST':
		if all([request.form['username'], request.form['password']]) and chkLogin(request.form['username'], request.form['password']):
			print(chkLogin(request.form['username'], request.form['password']))
			session['username'] = request.form["username"]
			return redirect("/notImpl/loggedIn")
		flash("authentication failure")
		return redirect("/login")#replace with correct call of render template?
	return render_template("login.html")#, name=user)

@app.route("/logout")
def logout():
	if 'username' in session:
		session.pop('username', None)
		return "Logged out sucessfull"
	else:
		return "You've been alredy logged out!"

#if __name__ == "__main__":
#	app.run(host='0.0.0.0')
