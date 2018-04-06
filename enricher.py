# enricher.py
# gordias
# By Markus Ehringer
# Date: 02.04.2018

import json
import time
import uuid
import db
import datacollector
import utils
from sources.source_class import Source 


field_list = ["contact_id", "first_name", "last_name", "email", "city", "country", "keywords", 
	"twitter_url", "crunchbase_url", "xing_url", "linkedin_url", "facebook_url", "profile_image_urls", "homepage", 
	"job", "orga_name", "orga_city", "orga_country", "orga_homepage", "orga_crunchbase_url", "last_sync", "sync_interval"] # TODO get database column names
contact_id_list = db.get_contact_ids()


def enrich_contacts(contact_list, age_str):
	enriched_contacts = dict()
	enriched_contact_list = list()

	for contact in contact_list:
		enriched_contact = enrich_contact(contact["first_name"], contact["last_name"], contact["organization"], age_str)
		enriched_contact_list.append(enriched_contact)

	return enriched_contact_list

def enrich_contact(first_name, last_name, organization, age_str):
	import notnull
	enriched_contact = None
	database_contact_list = db.get_contact_by_name(first_name, last_name, organization)
	timestamp = time.time()

	''' Check if data exists in database '''
	if database_contact_list:
		database_data = filter_contacts(database_contact_list, organization)
		
		database_contact = dict(database_data)
		del database_contact["contact_id"]
		del database_contact["last_sync"]
		del database_contact["sync_interval"]

		if age_str:
			age = float(age_str) * 60 * 60
		else:
			age = 604800.0 # = sec in a week

		''' Check if data in database is up-to-date '''
		if timestamp - float(database_data["last_sync"]) > age:
			''' Update contact '''
			contact_id = database_data["contact_id"]
			data = datacollector.collect_data(first_name, last_name, organization)
			contact_sync_interval = 0.0
			for source_name, source_data in data.items():
				db_source_contact = db.get_contact_by_contact_id(source_name, contact_id)
				source_contact = database_contact_to_contact_dict(db_source_contact)
				sync_interval = float(source_contact["sync_interval"])
				del source_contact["contact_id"]
				del source_contact["last_sync"]
				del source_contact["sync_interval"]
				if source_contact == source_data:
					sync_interval = sync_interval * 1.05
				else:
					sync_interval = sync_interval * 0.95
				''' Sync interval of merged contact is the minimum of the sync intervals of the sources '''
				if contact_sync_interval < sync_interval: 
					contact_sync_interval = sync_interval
				db.update_contact(source_name, contact_id, source_data, timestamp, sync_interval)
			
			notnull.update_nn_score_matrix(contact_id)
			enriched_contact = merge(data, database_contact, contact_id)
			db.update_contact("contacts", contact_id, enriched_contact, timestamp, contact_sync_interval)
		else:
			return database_contact
	else:
		''' Enrich contact '''
		data = datacollector.collect_data(first_name, last_name, organization)
		if not contact_found(data):
			return "{}"
		
		contact_id = (uuid.uuid1().int>>64) % 100000000
		request_data = dict()
		request_data["first_name"] = first_name
		request_data["last_name"] = last_name
		request_data["orga_name"] = organization

		notnull.add_person_to_matrices(contact_id)
		contact_id_list.append(contact_id)
		contact_sync_interval = 0.0

		for source_name, source_data in data.items():
			sync_interval = db.get_avg_sync_interval(source_name)
			''' Sync interval of merged contact is the minimum of the sync intervals of the sources '''
			if contact_sync_interval < sync_interval:
				contact_sync_interval = sync_interval
			if "first_name" not in source_data:
				source_data["first_name"] = first_name
			if "last_name" not in source_data:
				source_data["last_name"] = last_name
			db.write_contact(source_name, contact_id, source_data, timestamp, sync_interval)

		notnull.update_nn_score_matrix(contact_id)
		enriched_contact = merge(data, request_data, contact_id)
		if not enriched_contact["orga_name"]:
			enriched_contact["orga_name"] = organization
		db.write_contact("contacts", contact_id, enriched_contact, timestamp, contact_sync_interval)

	return enriched_contact

def enrich_contact_by_id(contact_id):
	database_contact = db.get_contact_by_contact_id("contacts", contact_id)
	contact = database_contact_to_contact_dict(database_contact)
	print(contact)
	enrich_contact(contact["first_name"], contact["first_name"], contact["orga_name"], "0")

def merge(data, base_data, contact_id):
	with open('field_merge_mapping.json', 'r') as field_merge_mapping_file:
		field_merge_mapping = json.load(field_merge_mapping_file)

	merged_data = dict()
	for field_name in field_list[1:-2]:	# Without contact_id, last_sync and sync_interval
		try:
			base_field_data = base_data[field_name]
			new_field = Field(base_field_data)
		except KeyError:
			new_field = Field()

		new_field.set_merge_function(field_merge_mapping[field_name])
		new_field_value_map = dict()
		
		for source in data.keys():
			fields = data[source]
			try:
				if not fields[field_name]:
					continue
				new_field_value_map[source] = fields[field_name]
			except KeyError:
				pass
		
		merged_data[field_name] = new_field.merge(contact_id, new_field_value_map)

	return merged_data

def filter_contacts(database_contact_list, organization):
	database_contact_dict_list = list()
	for database_contact in database_contact_list:
		database_contact_dict = database_contact_to_contact_dict(database_contact)
		database_contact_dict_list.append(database_contact_dict)
	
	if len(database_contact_dict_list) > 1:
		for database_contact_dict in database_contact_dict_list:
			if similar(organization, database_contact_dict["orga_name"], 2/3):
				return database_contact_dict
	else:
		return database_contact_dict_list[0]

def contact_found(data):
	for source_data in data.values():
		none_empty_contact_fields = {k: v for k, v in source_data.items() if v}
		if none_empty_contact_fields:
			return True
	return False

def database_contact_to_contact_dict(database_entry):
	''' Transform database contact entry to a contact dictionary '''
	database_contact_dict = dict()
	for i in range(0, len(field_list)):
		database_contact_dict[field_list[i]] = list(database_entry)[i]
	return database_contact_dict

class Field:

	def __init__(self, value = None):
		self.value = value

	def set_merge_function(self, merge_function_name):
		import merge_functions
		self.merge_function = getattr(merge_functions, merge_function_name)

	def merge(self, contact_id, source_field_map):
		return self.merge_function(contact_id, self.value, source_field_map)