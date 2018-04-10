# db_setup.py
# gordias
# By Markus Ehringer
# Date: 23.03.2018

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

def create_tables():
    print("Create tables")
    with open('sources/sourcesconfig.json', 'r') as sources_config_file:
        sources_config_json = json.load(sources_config_file)

    source_list = sources_config_json["sources"]
    
    sql_command_list = list()

    with open("tables_setup.sql", 'r') as sql_file:
        sql_commands = sql_file.read()
    sql_command_list = sql_command_list + sql_commands.split(';')

    for source in source_list:
        with open("sources/tables_setup.sql", 'r') as sql_file:
            sql_commands = sql_file.read()
        sql_command_list = sql_command_list + (sql_commands.replace("SOURCE", source["table_name"])).split(';')    
    
    cur = conn.cursor()
    for command in sql_command_list:
        cur.execute(command)

    cur.close()
    conn.commit()

def main():
	connect_to_database()
	create_tables()
	conn.close()

main()