# db_setup.py
# gordias
# By Markus Ehringer
# Date: 23.03.2018

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


def create_tables():
	print("create tables")
	cur = conn.cursor()

	command = """
        CREATE TABLE IF NOT EXISTS XXXXX (
                contact_id BIGINT PRIMARY KEY,
                first_name VARCHAR(25) NOT NULL,
                last_name VARCHAR(25) NOT NULL,
                email VARCHAR(75),
                city VARCHAR(25),
                country VARCHAR(25),
                keywords VARCHAR(250),
                twitter_url VARCHAR(100),
                crunchbase_url VARCHAR(100),
                xing_url VARCHAR(100),
                linkedin_url VARCHAR(100),
                facebook_url VARCHAR(100),
                profile_image_urls VARCHAR(250),
                homepage VARCHAR(100),
                job VARCHAR(50),
                orga_name VARCHAR(50),
                orga_city VARCHAR(25),
                orga_country VARCHAR(25),
                orga_homepage VARCHAR(100),
                orga_crunchbase_url VARCHAR(100),
                last_sync NUMERIC NOT NULL,
                sync_interval NUMERIC NOT NULL
        )
    """

	for table_name in table_names:
		cur.execute(command.replace("XXXXX", table_name))
	
	cur.close()
	conn.commit()


def main():
	connect_to_database()
	create_tables()
	conn.close()

main()