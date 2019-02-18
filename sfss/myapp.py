#!/usr/bin/env python3

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def hi():
	return "Hello World, how are you! Is the program waiting for changes?"

@app.route("/login/", methods=["POST", "GET"])
def login():
	if request.method == 'POST':
		return request.form["username"]
	return render_template("login.html")#, name=user)
	

#if __name__ == "__main__":
#	app.run(host='0.0.0.0')
