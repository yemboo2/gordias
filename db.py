# db.py
# gordias
# By Markus Ehringer
# Date: 02.04.2018

import psycopg2
import json

DEFAULT_SYNC_INTERVAL = 24.0 * 60 * 60 # in s

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

def get_contact_by_name(first_name, last_name, company = ""):
	cur = conn.cursor()
	cur.execute("SELECT * FROM contacts WHERE " + "first_name = '" + first_name.strip('\'') 
		+ "' AND last_name = '" + last_name.strip('\'') + "'")
	rows = cur.fetchall() # list of tuples
	cur.close()

	return rows

def get_contact_by_contact_id(table_name, contact_id):
	cur = conn.cursor()
	cur.execute("SELECT * FROM " + table_name.lower() + " WHERE " + "contact_id = " + str(contact_id))
	rows = cur.fetchall() # list of tuples
	cur.close()

	if rows:
		return list(rows[0])
	else:
		return rows

def get_contact_ids():
	cur = conn.cursor()
	cur.execute("SELECT contact_id FROM contacts")
	rows = cur.fetchall()
	contact_id_list = list(map(lambda x: x[0], rows))
	cur.close()

	return contact_id_list

def get_sync_fields():
	cur = conn.cursor()
	cur.execute("SELECT contact_id, last_sync, sync_interval FROM contacts")
	rows = cur.fetchall()
	cur.close()

	return rows

def get_avg_sync_interval(table_name):
	cur = conn.cursor()
	cur.execute("SELECT AVG (sync_interval) FROM " + table_name)
	rows = cur.fetchall()
	cur.close()

	if rows[0][0]:
		return float(rows[0][0])
	else:
		return DEFAULT_SYNC_INTERVAL


def write_contact(table_name, contact_id, contact, timestamp, sync_interval):
	cur = conn.cursor()
	none_empty_contact_fields = {k: v for k, v in contact.items() if v}
	fields_str = ', '.join(list(none_empty_contact_fields.keys()))
	if fields_str:
		fields_str += ", "
	values_str = "', '".join(list(none_empty_contact_fields.values()))
	if values_str:
		values_str = "'" + values_str + "', "

	cur.execute("INSERT INTO " + table_name.lower() + " (contact_id, " + fields_str + "last_sync, sync_interval) VALUES (" 
		+ str(contact_id) + ", " + values_str + str(timestamp) + ", " + str(sync_interval) + ")")
	
	conn.commit()
	cur.close()


def update_contact(table_name, contact_id, contact, timestamp, sync_interval):
	cur = conn.cursor()
	none_empty_contact_fields = {k: v for k, v in contact.items() if v}
	changed_fields = list()
	
	for field_name, value in none_empty_contact_fields.items():
		changed_fields.append(field_name + " = '" + value + "'")
	changed_fields.append("last_sync" + " = '" + str(timestamp) + "'")
	changed_fields.append("sync_interval" + " = '" + str(sync_interval) + "'")
	
	if changed_fields:
		cur.execute("UPDATE " + table_name.lower() + " SET " + ', '.join(changed_fields) + " WHERE contact_id = " + str(contact_id))
	
	conn.commit()
	cur.close()

def close_connection():
	conn.close()


connect_to_database()