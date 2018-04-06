# db_drop.py
# gordias
# By Markus Ehringer
# Date: 24.03.2018

import psycopg2
import json

table_names = ["contacts", "twitter", "crunchbase"]

def connect_to_database():
	global conn
	with open('../database_config.json', 'r') as database_config_file:
		database_config_json = json.load(database_config_file)
	
	try:
		conn = psycopg2.connect("dbname='" + database_config_json["dbname"] + 
								"' user='" + database_config_json["user"] + 
								"' host='" + database_config_json["host"] + 
								"' password='" + database_config_json["password"] + "'")
	except Exception as e:
		raise e


def drop_truncate_tables():
	print("drop/truncate tables")
	cur = conn.cursor()
	command = "DROP TABLE \"XXXXX\""

	for table_name in table_names:
		cur.execute(command.replace("XXXXX", table_name))
	
	cur.close()
	conn.commit()


def main():
	connect_to_database()
	drop_truncate_tables()
	conn.close()

main()