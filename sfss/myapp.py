#!/usr/bin/env python3

from flask import Flask, render_template, request, session, escape, url_for, redirect, g
import random
import pymysql



app = Flask(__name__)
app.config.update(
	SECRET_KEY = '\x81H\xb8\xa3S\xf8\x8b\xbd"o\xca\xd7\x08\xa4op\x07\xb5\xde\x87\xb8\xcc\xe8\x86\\\xffS\xea8\x86"\x97'
)

def getDBCursor():
	if not hasattr(g, 'db'):
		g.db = pymysql.connect(user='sfss', password='QsbPu7N0kJ4ijyEf', db='sfss', cursorclass=pymysql.cursors.DictCursor)
	return g.db.cursor()

@app.teardown_appcontext
def closeDB(error):
	print(error)
	if hasattr(g, 'db'):
		g.db.commit()
		g.db.close()

def rndFill():
	cursor = getDBCursor()
	for i in range (100):
		cursor.execute("INSERT INTO users (username, password) VALUES ({0}, PASSWORD({0}))".format(i))
	cursor.close()

def registerUser(username, password, firstName="null", lastName="null", email="null", enabled=1):
	cursor = getDBCursor()
	cursor.execute("INSERT INTO users (username, password, firstName, lastName, email, enabled) VALUES (\'{0}\', PASSWORD(\'{1}\'), \'{2}\', \'{3}\', \'{4}\', \'{5}\')".format(username, password, firstName, lastName, email, enabled))
	cursor.close()

def chkLogin(username, password):
	cursor = getDBCursor()
	cursor.execute("SELECT id FROM users WHERE username=\'{0}\' AND password=PASSWORD(\'{1}\')".format(username, password))
	res = cursor.fetchall() != {}
	cursor.close()
	return res

@app.route("/")
def hi():
	print(chkLogin("User1", "Versuch"))
	return "Hello World, how are you! Is the program waiting for changes?"
	


@app.route("/notImpl/<item>")
def notImpl(item):
	return "The requestet site or service {0} hasn't been implemented yet".format(item)


@app.route("/login/", methods=["POST", "GET"])
def login():
	if 'username' in session:
		return redirect('/notImpl/loggedIn')
	if request.method == 'POST':
		session['username'] = request.form["username"]
		return request.form["username"]
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
