# enricher.py
# gordias
# By Markus Ehringer
# Date: 26.03.2018

import json
import time
import uuid
import db
import datacollector
import merge_functions
import utils

field_list = ["contact_id", "first_name", "last_name", "email", "city", "country", "keywords", 
	"twitter_url", "crunchbase_url", "xing_url", "linkedin_url", "facebook_url", "image_urls", "homepage", 
	"job", "orga_name", "orga_city", "orga_country", "orga_homepage", "orga_crunchbase_url", "last_sync"]

def enrich_contacts(contact_list, age_str):
	enriched_contacts = dict()
	enriched_contact_list = list()

	for contact in contact_list:
		enriched_contact = enrich_contact(contact["first_name"], contact["last_name"], contact["organization"], age_str)
		enriched_contact_list.append(enriched_contact)

	return enriched_contact_list

def enrich_contact(first_name, last_name, organization, age_str):
	enriched_contact = None
	database_contact_list = db.get_contact(first_name, last_name, organization)
	timestamp = time.time()

	''' Check if data exists in database '''
	if database_contact_list:
		database_data = get_database_contact(database_contact_list, organization)
		
		database_contact = dict(database_data)
		del database_contact["contact_id"]
		del database_contact["last_sync"]

		if age_str:
			age = float(age_str) * 60 * 60
		else:
			age = 604800.0 # = sec in a week

		''' Check if data in database is up-to-date '''
		if timestamp - float(database_data["last_sync"]) > age:
			''' Enrich contact '''
			data = datacollector.collect_data(first_name, last_name, organization)			
			enriched_contact = merge(data, database_contact)
			db.update_contact(database_data["contact_id"], enriched_contact, database_contact, timestamp)
		else:
			return database_contact
	else:
		''' Enrich contact '''
		data = datacollector.collect_data(first_name, last_name, organization)
		
		request_data = dict()
		request_data["first_name"] = first_name
		request_data["last_name"] = last_name
		request_data["orga_name"] = organization

		enriched_contact = merge(data, request_data)
		contact_id = (uuid.uuid1().int>>64) % 100000000
		db.write_contact(contact_id, enriched_contact, timestamp)

	return enriched_contact


def merge(data, base_data):
	with open('field_merge_mapping.json', 'r') as field_merge_mapping_file:
		field_merge_mapping = json.load(field_merge_mapping_file)

	merged_data = dict()
	for field_name in field_list[1:-1]:	# Without contact_id and sync-timestamp
		# TODO When using weight matrix save fieldname in global variable so it can be used on other file or pass to merge function?
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
		
		merged_data[field_name] = new_field.merge(new_field_value_map)

	return merged_data


def get_database_contact(database_contact_list, organization):
	database_contact_dict_list = list()
	for database_contact in database_contact_list:
		database_contact_dict = dict()
		for i in range(0, len(field_list)):
			database_contact_dict[field_list[i]] = list(database_contact)[i]
		database_contact_dict_list.append(database_contact_dict)
	
	if len(database_contact_dict_list) > 1:
		for database_contact_dict in database_contact_dict_list:
			if similar(organization, database_contact_dict["orga_name"], 2/3):
				return database_contact_dict
	else:
		return database_contact_dict_list[0]


class Field:

	def __init__(self, value = None):
		self.value = value

	def set_merge_function(self, merge_function_name):
		self.merge_function = getattr(merge_functions, merge_function_name)

	def merge(self, source_field_map):
		return self.merge_function(self.value, source_field_map)