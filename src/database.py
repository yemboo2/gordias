# database.py
# gordias
# By Markus Ehringer
# Date: 16.04.2018

import psycopg2
import json
import utils
import os
import time
import logging

DEFAULT_SYNC_INTERVAL = 7.0 * 24 * 60 * 60 # 1 week in seconds

def connect_to_database():
	global conn
	
	db_name = os.getenv("DB_NAME", "gordias_test")
	db_user = os.getenv("DB_USER", "gordias1")
	db_host = os.getenv("DB_HOST", "localhost")
	db_password = os.getenv("DB_PASSWORD", "pg55_2.0")

	while True:
		try:
			time.sleep(3)
			conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(db_name, db_user, db_host, db_password))
			logging.info("Database connected")
			break
		except Exception as e:
			logging.exception("dbname='{}' user='{}' host='{}' password='{}'".format(db_name, db_user, db_host, db_password))

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
	
	''' Match the remaining contacts' organization field to get a contact-ID'''
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

	# retrieve data from contacts table
	rows = get("contacts", "last_sync, sync_interval", "contact_id = '{}'".format(contact_id))
	if not rows:
		return tuple([None]*4)
	contact_last_sync = rows[0][0]
	contact_sync_interval = rows[0][1]

	# retrieve all fields in contacts_values tables
	contact_data = get_contact_values("contacts_values", "contact_id = '{}'".format(contact_id))

	return contact_id, contact_data, contact_last_sync, contact_sync_interval

def get_contact_by_contact_id(contact_id):
	# retrieve all fields in contacts_values tables
	contact_data = get_contact_values("contacts_values", "contact_id = '{}'".format(contact_id))
	return contact_data

def get_source_contact_by_id(source_name, contact_id):
	# retrieve sync_interval from contacts table
	rows = get("sources_contacts", "sync_interval", "contact_id = '{}' AND source_name = '{}'".format(contact_id, source_name))
	if not rows:
		return tuple([None]*2)
	contact_sync_interval = rows[0][0]

	# retrieve all fields in sources_contacts_values tables
	contact_data = get_contact_values("sources_contacts_values", "contact_id = {} AND source_name = '{}'".format(contact_id, source_name))
	return contact_data, contact_sync_interval

def get_contact_values(table_name, where):
	# retrieve all fields from xxx_values table
	contact_data = dict()
	rows = get(table_name, "field_name, value", where)
	for row in rows:
		contact_data[row[0]] = row[1]
	return contact_data

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

def get_avg_source_sync_interval(source_name):
	cur = conn.cursor()
	cur.execute("SELECT AVG (sync_interval) FROM sources_contacts WHERE source_name = '{}'".format(source_name))
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

def write_contact(contact_id, data, last_sync, sync_interval):
	write("contacts", "contact_id, last_sync, sync_interval", "{}, {}, {}".format(contact_id, last_sync, sync_interval))
	for field_name, value in data.items():
		write("contacts_values", "contact_id, field_name, value", "{}, '{}', '{}'".format(contact_id, field_name, value))
	conn.commit()

def write_source_contact(source_name, contact_id, source_data, sync_interval):
	write("sources_contacts", "contact_id, source_name, sync_interval", "{}, '{}', {}".format(contact_id, source_name, sync_interval))
	for field_name, value in source_data.items():
		write("sources_contacts_values", "contact_id, source_name, field_name, value", "{}, '{}', '{}', '{}'".format(contact_id, source_name, field_name, value))
	conn.commit()
	
def write(table_name, columns, values):
	cur = conn.cursor()
	cur.execute("INSERT INTO {} ({}) VALUES ({})".format(table_name, columns, values))
	cur.close()

### UPDATE ###

def update_contact(contact_id, data, last_sync, sync_interval):
	update("contacts", ["last_sync", "sync_interval"], [last_sync, sync_interval], "contact_id = {}".format(contact_id))
	for field_name, value in data.items():
		update("contacts_values", ["value"], [value], "contact_id = {} AND field_name = '{}'".format(contact_id, field_name))
	conn.commit()

def update_source_contact(source_name, contact_id, source_data, sync_interval):
	update("sources_contacts", ["sync_interval"], [sync_interval], "contact_id = {} AND source_name = '{}'".format(contact_id, source_name))
	for field_name, value in source_data.items():
		update("sources_contacts_values", ["value"], [value], "contact_id = {} AND source_name = '{}' AND field_name = '{}'".format(contact_id, source_name, field_name))
	conn.commit()

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