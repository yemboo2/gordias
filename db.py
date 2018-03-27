# api.py
# gordias
# By Markus Ehringer
# Date: 13.03.2018

import psycopg2
import json

def connect_to_database():
	global conn
	with open('database_config.json', 'r') as database_config_file:
		database_config_json = json.load(database_config_file)
	
	try:
		conn = psycopg2.connect("dbname='" + database_config_json["dbname"] + 
								"' user='" + database_config_json["user"] + 
								"' host='" + database_config_json["host"] + 
								"' password='" + database_config_json["password"] + "'")
	except Exception as e:
		raise e


def get_contact(first_name, last_name, company = ""):
	cur = conn.cursor()
	cur.execute("SELECT * FROM contacts WHERE " + "first_name = '" + first_name.strip('\'') 
		+ "' AND last_name = '" + last_name.strip('\'') + "'")
	rows = cur.fetchall() # list of tuples
	cur.close()

	return rows


def write_contact(id, contact, timestamp):
	cur = conn.cursor()
	none_empty_contact_fields = {k: v for k, v in contact.items() if v}
	values_str = "'" + "', '".join(list(none_empty_contact_fields.values())) + "'"
	
	cur.execute("INSERT INTO contacts (contact_id, " + ', '.join(list(none_empty_contact_fields.keys())) 
		+ ", last_sync) VALUES (" + str(id) + ", " + values_str + ", " + str(timestamp) + ");")
	
	conn.commit()
	cur.close()


def update_contact(id, enriched_contact, database_contact, timestamp):
	cur = conn.cursor()
	none_empty_contact_fields = {k: v for k, v in enriched_contact.items() if v}
	changed_fields = dict()
	
	for field_name, value in none_empty_contact_fields.items():
		if enriched_contact[field_name] != database_contact[field_name]:
			changed_fields.append(field_name + " = '" + enriched_contact[field_name] + "'")
	
	if changed_fields:
		cur.execute("UPDATE contacts SET " + ' '.join(changed_fields) + " WHERE contact_id = " + str(id))
	
	conn.commit()
	cur.close()

def close_connection():
	conn.close()


connect_to_database()