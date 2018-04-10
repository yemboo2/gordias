# enricher.py
# gordias
# By Markus Ehringer
# Date: 08.04.2018

import json
import time
import uuid
import database
import datacollector
import utils
import notnull
from functools import reduce

def enrich_contacts(contact_list, age_str):
	enriched_contact_list = list()

	for contact in contact_list:
		enriched_contact = enrich_contact(contact["first_name"], contact["last_name"], contact["organization"], age_str)
		enriched_contact_list.append(enriched_contact)

	return enriched_contact_list

def enrich_contact_by_id(contact_id):
	contact = database.get_contact_by_contact_id(contact_id)	
	enrich_contact(contact["first_name"], contact["first_name"], contact["orga_name"], "0")

def enrich_contact(first_name, last_name, organization, age_str):
	timestamp = time.time()
	
	contact_id, database_contact_data, contact_last_sync, contact_sync_interval = \
		database.get_contact_by_name(first_name, last_name, organization)

	''' Check if data exists in database '''
	if database_contact_data:
		print("update")
		if age_str:
			age = float(age_str) * 60 * 60
		else:
			age = 604800.0 # = sec in a week

		''' Check if data in database is up-to-date '''
		if timestamp - float(contact_last_sync) > age:
			''' Update contact '''
			data = datacollector.collect_data(first_name, last_name, organization)
			min_sync_interval = float("Inf")
			''' Update source contacts'''
			for source_name, source_contact_data in data.items():
				contactid, database_source_contact_data, source_contact_last_sync, source_contact_sync_interval = \
					database.get_contact_by_id(source_name, contact_id)
				sync_interval = float(source_contact_sync_interval)
				if database_source_contact_data == source_contact_data:
					sync_interval = sync_interval * 1.05
				else:
					sync_interval = sync_interval * 0.95
				''' Sync interval of merged contact is the minimum of the sync intervals of the sources '''
				if min_sync_interval > sync_interval: 
					min_sync_interval = sync_interval
				database.update_source_contact(source_name, contact_id, source_contact_data, sync_interval)
			
			notnull.update_nn_score_matrix(contact_id)
			enriched_contact = merge(contact_id, database_contact_data, data)
			database.update_contact(contact_id, enriched_contact, timestamp, min_sync_interval)
			return enriched_contact
		else:
			return database_contact_data
	else:
		''' Enrich contact '''
		data = datacollector.collect_data(first_name, last_name, organization)
		data = dict(list(filter(lambda z: bool(z[1]), data.items())))
		print("{} {} - {}".format(first_name, last_name, list(map(lambda x: x[0], data.items()))))
		''' Check if at least one source could get some data '''
		if not data:
			return "{}"
		
		contact_id = (uuid.uuid1().int>>64) % 100000000
		request_data = dict()
		request_data["first_name"] = first_name
		request_data["last_name"] = last_name
		request_data["orga_name"] = organization

		notnull.add_contact_to_matrices(contact_id)
		contact_sync_interval = 0.0

		for source_name, source_data in data.items():
			sync_interval = database.get_avg_sync_interval(source_name)
			''' Sync interval of merged contact is the minimum of the sync intervals of the sources '''
			if contact_sync_interval < sync_interval:
				contact_sync_interval = sync_interval
				
			database.write_source_contact(source_name, contact_id, source_data, sync_interval)

		notnull.update_nn_score_matrix(contact_id)
		enriched_contact = merge(contact_id, request_data, data)
		database.write_contact(contact_id, enriched_contact, timestamp, contact_sync_interval)
		return enriched_contact

def merge(contact_id, base_data, data):
	with open('field_merge_mapping.json', 'r') as field_merge_mapping_file:
		field_merge_mapping = json.load(field_merge_mapping_file)

	merged_data = dict()
	for field_name in field_merge_mapping.keys():
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
				new_field_value_map[source] = fields[field_name]
			except KeyError:
				pass
		
		merged_value = new_field.merge(contact_id, new_field_value_map)
		if merged_value:
			merged_data[field_name] = merged_value

	return merged_data

class Field:

	def __init__(self, value = None):
		self.value = value

	def set_merge_function(self, merge_function_name):
		import merge_functions
		self.merge_function = getattr(merge_functions, merge_function_name)

	def merge(self, contact_id, source_field_map):
		return self.merge_function(contact_id, self.value, source_field_map)
