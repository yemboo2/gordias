# database.py
# gordias
# By Markus Ehringer
# Date: 07.04.2018

import psycopg2
import json
import utils

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

### SELECT ###

def get_contact_by_name(first_name, last_name, organization_name):
	''' Get contact_ids matching first name '''
	rows = get("contacts_values", "contact_id", "field_name = '{}' AND value = '{}'".format('first_name', first_name))
	if not rows:
		return tuple([None]*4)	# Contact not in database

	first_name_contact_id_list = list(map(lambda x: x[0], rows))
	
	''' Get contact_ids matching last name '''
	rows = get("contacts_values", "contact_id", "field_name = '{}' AND value = '{}'".format('last_name', last_name))
	if not rows:
		return tuple([None]*4)

	last_name_contact_id_list = list(map(lambda x: x[0], rows))
	name_contact_id_list = set(first_name_contact_id_list).intersection(last_name_contact_id_list)
	
	contact_id = None
	if len(name_contact_id_list) == 1:
		contact_id = list(name_contact_id_list)[0]
	for tmp_contact_id in name_contact_id_list:
		rows = get("contacts_values", "value", "contact_id = '{}' AND field_name = '{}'".format(tmp_contact_id, 'orga_name'))
		if rows:
			if utils.sim(rows[0][0], organization_name, 2/3):
				contact_id = tmp_contact_id
				break

	if not contact_id:
		return tuple([None]*4)

	return get_contact_by_id('contacts', contact_id)
	
def get_contact_by_id(table_name, contact_id):
	# retrieve data from contacts table
	rows = get(table_name, '*', "contact_id = '{}'".format(contact_id))
	if not rows:
		return tuple([None]*4)
	contact_last_sync = rows[0][1]
	contact_sync_interval = rows[0][1]

	# retrieve all fields in contacts_values tables
	contact_data = dict()
	values_table_name = table_name + "_values"
	rows = get(table_name + "_values", "field_name, value", "contact_id = '{}'".format(contact_id))
	for row in rows:
		contact_data[row[0]] = row[1]

	return contact_id, contact_data, contact_last_sync, contact_sync_interval

def get(table_name, columns, where):
	cur = conn.cursor()
	cur.execute("SELECT {} FROM {} WHERE {}".format(columns, table_name, where))
	rows = cur.fetchall() # list of tuples
	cur.close()
	return rows

def get_contact_ids():
	cur = conn.cursor()
	cur.execute("SELECT contact_id FROM contacts")
	rows = cur.fetchall()
	contact_id_list = list(map(lambda x: x[0], rows))
	cur.close()
	return contact_id_list

def get_avg_sync_interval(table_name):
	cur = conn.cursor()
	cur.execute("SELECT AVG (sync_interval) FROM {}".format(table_name))
	rows = cur.fetchall()
	cur.close()

	if rows[0][0]:
		return float(rows[0][0])
	else:
		return DEFAULT_SYNC_INTERVAL

def get_sync_fields():
	cur = conn.cursor()
	cur.execute("SELECT * FROM contacts")
	rows = cur.fetchall()
	cur.close()
	return rows

### WRITE ###

def write_contact(contact_id, source_data, last_sync, sync_interval):
	write("contacts", "contact_id, last_sync, sync_interval", "{}, {}, {}".format(contact_id, last_sync, sync_interval))
	write_contact_values("contacts_values", contact_id, source_data)
	conn.commit()

def write_source_contact(table_name, contact_id, source_data, sync_interval):
	write(table_name, "contact_id, sync_interval", "{}, {}".format(contact_id, sync_interval))
	write_contact_values(table_name + "_values", contact_id, source_data)
	conn.commit()
	
def write_contact_values(table_name, contact_id, data):
	cur = conn.cursor()
	for field_name, value in data.items():
		write(table_name, "contact_id, field_name, value", "{}, '{}', '{}'".format(contact_id, field_name, value))
	cur.close()

def write(table_name, columns, values):
	cur = conn.cursor()
	cur.execute("INSERT INTO {} ({}) VALUES ({})".format(table_name, columns, values))
	cur.close()

### UPDATE ###

def update_contact(contact_id, source_data, last_sync, sync_interval):
	update("contacts", ["last_sync", "sync_interval"], [last_sync, sync_interval], "contact_id = {}".format(contact_id))
	update_contact_values("contacts_values", contact_id, source_data)
	conn.commit()

def update_source_contact(table_name, contact_id, source_data, sync_interval):
	update(table_name, ["sync_interval"], [sync_interval], "contact_id = {}".format(contact_id))
	update_contact_values(table_name + "_values", contact_id, source_data)
	conn.commit()
	
def update_contact_values(table_name, contact_id, data):
	cur = conn.cursor()
	for field_name, value in data.items():
		update(table_name, ["value"], [value], "contact_id = {} AND field_name = '{}'".format(contact_id, field_name))
	cur.close()

def update(table_name, columns, values, where):
	cur = conn.cursor()
	column_value_str_list = list()
	for column, value in list(zip(columns, values)):
		column_value_str_list.append("{} = '{}'".format(column, value))
	cur.execute("UPDATE {} SET {} WHERE {}".format(table_name,', '.join(column_value_str_list), where))
	cur.close()


def close_connection():
	conn.close()


connect_to_database()