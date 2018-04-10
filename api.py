# api.py
# gordias
# By Markus Ehringer
# Date: 29.03.2018

import enricher
import json
from bottle import route, request

@route('/contact', method = 'POST')
def post_contact():
	first_name = request.forms.get('first_name')
	last_name = request.forms.get('last_name')
	organization = request.forms.get('organization')
	age = request.forms.get('age')	# in hours
	
	contact = dict()
	if bool(last_name) & bool(first_name):	# Only continue if at least first_name and last_name are not empty 
		contact["data"] = enricher.enrich_contact(first_name, last_name, organization, age)
	
	return contact
	

@route('/')
@route('/contacts', method = 'POST')
def post_contacts():
	data = request.forms.get('contacts')
	age = request.forms.get('age')
	print()
	contact_list = (json.loads(data))["contacts"]
	contacts = dict()
	contacts["data"] = enricher.enrich_contacts(contact_list, age)

	return contacts

@route('/contact/id', method = 'PUT')
def sync_contact():
	contact_id = request.forms.get('contact_id')
	enricher.enrich_contact_by_id(contact_id)

@route('/contacted', method = 'GET')
def test():
	return "Hallo"