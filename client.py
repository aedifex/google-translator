#!/usr/bin/env python

# Simple client to interface with Google Translate API
# target == to
# text   == from
# translate_text("en", text)
# list_languages()

import argparse
import os
import json
from flask import Flask, render_template, request



if os.getenv("WEB_SERVER"):
	WEB_SERVER = True
else:
	WEB_SERVER = False

# Courtesy of:
# https://stackoverflow.com/questions/5508509/how-do-i-check-if-a-string-is-valid-json-in-python
def is_json(json):
	try:
		json.loads(json)
	except ValueError as e:
		return False
	return True

# reads json, returns data
def read_file(file_name):
	data_file = open(file_name)
	data = json.load(data_file)
	# print(data["q"])
	return data["q"]

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
	# print("Result: \"{}\"".format(result["translatedText"]))
	return result["translatedText"]

# [START translate_list_codes]

"""
def list_languages():
    # Lists all available languages.
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    results = translate_client.get_languages()

    for language in results:
        print(u"{name} ({language})".format(**language))

# [END translate_list_codes]
"""

parser = argparse.ArgumentParser()

# ??? subparsers
# ??? command
subparsers = parser.add_subparsers(dest="command")
translate_text_parser = subparsers.add_parser("translate-text")

# order of operations matters
translate_text_parser.add_argument("text")

parser.add_argument("-d")

args = parser.parse_args()

if args.command == "translate-text":
	translate_text("en", args.text)
# ???
elif args.d:
	# print(read_file(args.d))
	if is_json(args.d):
		translate_text("en", read_file(args.d))

# Web Server
app = Flask(__name__)

@app.route('/translate', methods=["POST"])
def translate_api():
	# Returns a dictionary
	data = request.get_json()
	key = "q"

	# Check if key is present
	# Also check if string has any malformed characters
	if not key in data:
		return("Key not found...") 
	query = data[key]
	translated_text = translate_text("en", query)
	return(translated_text)

if WEB_SERVER:
	app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT",1989)))
