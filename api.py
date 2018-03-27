# api.py
# gordias
# By Markus Ehringer
# Date: 21.03.2018

import enricher
import json
from bottle import run, route, request


@route('/contact', method = 'POST')
def post_contact():
	first_name = request.forms.get('first_name')
	last_name = request.forms.get('last_name')
	organization = request.forms.get('organization')
	age = request.forms.get('age')	# in hours
	
	contact = dict()
	if bool(last_name) & bool(first_name):	# Only continue if at least first_name and last_name are not empty 
		contact["data"] = enricher.enrich_contact(ffirst_name, last_name, organization, age)
	
	return contact
	

@route('/')
@route('/contacts', method = 'POST')
def post_contacts():
	data = request.forms.get('contacts')
	age = request.forms.get('age')
	
	contact_list = (json.loads(data))["contacts"]
	contacts = dict()
	contacts["data"] = enricher.enrich_contacts(contact_list, age)

	return contacts


def start():
	run(host = "localhost", port = 8080)