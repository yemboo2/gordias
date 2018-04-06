# sync.py
# gordias
# By Markus Ehringer
# Date: 29.03.2018

import requests
from bottle import run, route, request
import time
import db

URL_OWN_API = 'http://localhost:8080/contact/id'

def start_sync():
	time.sleep(1)
	sync_dict = get_sync_dict()
	''' Wait until there are any contacts in the database '''
	while not sync_dict:	
		time.sleep(1)

	while True:
		sync_dict = get_sync_dict()
		contact_id = min(sync_dict, key=sync_dict.get)
		next_sync_time = sync_dict[contact_id]
		if next_sync_time <= 0:
			response = requests.post(URL_OWN_API, data={'contact_id' : contact_id})
		else:
			time.sleep(next_sync_time)	

def get_sync_dict():
	sync_dict = dict()
	timestamp = time.time()
	rows = db.get_sync_fields()

	for row in rows:
		next_sync_time = int((float(row[1]) + (float(row[2]))) - float(timestamp))
		sync_dict[row[0]] = int((float(row[1]) + (float(row[2]))) - float(timestamp))	# (last_sync + sync_interval) - current time

	return sync_dict 