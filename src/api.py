# api.py
# gordias
# By Markus Ehringer
# Date: 16.04.2018

import json
import logging
from bottle import route, request
import enricher

@route('/contact', method = 'POST')
def post_contact():
	logging.info("API request '/contact'-endpoint")
	try:
		first_name = request.forms.get('first_name')
		last_name = request.forms.get('last_name')
		organization = request.forms.get('organization')
		age = request.forms.get('age')	# in hours
		
		contact = dict()
		if bool(last_name) & bool(first_name) & bool(organization):	# Only continue if first_name, last_name and organization are not empty
			contact["data"] = enricher.enrich_contact(first_name, last_name, organization, age)
		return contact
	except Exception as e:
		logging.exception(str(e))
		return dict()
	
@route('/')
@route('/contacts', method = 'POST')
def post_contacts():
	logging.info("API request '/contacts'-endpoint")
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

@route('/contact/id', method = 'POST')
def sync_contact():
	contact_id = request.forms.get('contact_id')
	logging.info("Sync, id = {}".format(contact_id))
	enricher.enrich_contact_by_id(contact_id)
	return dict()