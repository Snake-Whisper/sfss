#!/usr/bin/env python3

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hi():
	return "Hello World, how are you! Is the program waiting for changes?"
if __name__ == "__main__":
	app.run(host='0.0.0.0')
