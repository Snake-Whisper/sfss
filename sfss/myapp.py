#!/usr/bin/env python3

from flask import Flask, render_template, request, session, escape, url_for, redirect, g
app = Flask(__name__)
app.secret_key = '\x81H\xb8\xa3S\xf8\x8b\xbd"o\xca\xd7\x08\xa4op\x07\xb5\xde\x87\xb8\xcc\xe8\x86\\\xffS\xea8\x86"\x97'

def getDB():
	if not hasattr(g, 'db'):
		g.db = pymysql.connect(user='sfss', password='QsbPu7N0kJ4ijyEf', db='sfss', cursorclass=pymysql.cursors.DictCursor)
	return g.db

@app.teardown_appcontext
def closeDB():
	if hasattr(g, 'db'):
		db.close()
		

@app.route("/")
def hi():
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
