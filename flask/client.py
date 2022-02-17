#!/usr/bin/env python

# Aedifex MMXXII
# Simple client to interface with Google Translate API
# target == to
# text   == from
# primary function: e.g. translate_text("en", text)
# auxiliary functions: list_languages()

import argparse
import os
import json
from flask import Flask, render_template, request

if os.getenv("WEB_SERVER"):
	WEB_SERVER = True
else:
	WEB_SERVER = False

def translate_text(target, text):
	"""Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
	import six
	from google.cloud import translate_v2 as translate

	translate_client = translate.Client()

	# ???
	if isinstance(text, six.binary_type):
		# as opposed to ASCII??
		text = text.decode("utf-8")

	# Returned result is a dictionary
	# with the following keys: 
	# dict_keys(['translatedText', 'detectedSourceLanguage', 'input'])
	# Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
	result = translate_client.translate(text,target_language=target)
	return result["translatedText"]

parser = argparse.ArgumentParser()

# ??? subparsers
# ??? command
subparsers = parser.add_subparsers(dest="command")
translate_text_parser = subparsers.add_parser("translate-text")

# order of operations matters
translate_text_parser.add_argument("text")
translate_text_parser.add_argument("-s", "--speak", required=False, action="store_true")

parser.add_argument("-d")

args = parser.parse_args()

if args.command == "translate-text":
	if args.speak:
		os.system("say " + str(translate_text("la", args.text)))
	else:
		print(translate_text("en", args.text))
else:
	print("Need to enter a command...")

# Web Server
app = Flask(__name__)

@app.route('/translate', methods=["GET", "POST"])
def translate_api():
	# Returns a dictionary
	data = request.get_json()
	print(data)
	
	if len(request.form) > 0:
		query = request.form["text"]
	else:
		query = ""
	return render_template("index.html", data=translate_text("en", query))

if WEB_SERVER:
	app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT",1989)))
