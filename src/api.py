# api.py
# gordias
# By Markus Ehringer
# Date: 29.03.2018

import json
import logging
from bottle import route, request
import enricher

@route('/contact', method = 'POST')
def post_contact():
	try:
		first_name = request.forms.get('first_name')
		last_name = request.forms.get('last_name')
		organization = request.forms.get('organization')
		age = request.forms.get('age')	# in hours
		
		contact = dict()
		if bool(last_name) & bool(first_name):	# Only continue if at least first_name and last_name are not empty
			contact["data"] = enricher.enrich_contact(first_name, last_name, organization, age)
		return contact
	except Exception as e:
		logging.exception(str(e))
		return dict()
	
@route('/')
@route('/contacts', method = 'POST')
def post_contacts():
	try:
		data = request.forms.get('contacts')
		age = request.forms.get('age')

		contact_list = (json.loads(data))["contacts"]
		contacts = dict()
		contacts["data"] = enricher.enrich_contacts(contact_list, age)
		return contacts
	except Exception as e:
		logging.exception(str(e))
		return dict()

@route('/contact/id', method = 'PUT')
def sync_contact():
	contact_id = request.forms.get('contact_id')
	enricher.enrich_contact_by_id(contact_id)

@route('/contacted', method = 'GET') #TODO
def test():
	return "Hallo"